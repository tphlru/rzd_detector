import dgl
import torch
from dgl.data import DGLDataset
from torch.nn import DataParallel

# from torch.utils.data import DataLoader
from dgl.dataloading import GraphDataLoader
from torch.utils.data.sampler import SubsetRandomSampler

import torch.nn as nn
import torch.nn.functional as F
from dgl.nn.pytorch import GINConv
from dgl.nn.pytorch.glob import SumPooling
import torch.optim as optim
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel
from dgl.data import split_dataset


from tqdm import tqdm


import os
import sys

os.environ["DGLBACKEND"] = "pytorch"


def init_process_group(world_size, rank):
    dist.init_process_group(
        backend="nccl",  # 'nccl' для нескольких GPU
        init_method="tcp://127.0.0.1:14048",  # Уникальный адрес и порт
        world_size=world_size,
        rank=rank,
    )


# Путь к сохраненным файлам
graph_path = "saved_graphs.dgl"
label_path = "saved_labels.pt"


class CustomGraphDataset(DGLDataset):
    def __init__(self):
        super().__init__(name="custom_graph")

    def process(self):
        self.graphs, _ = dgl.load_graphs(graph_path)
        self.labels = torch.load(label_path)

        for graph in self.graphs:
            num_nodes = graph.number_of_nodes()
            # Создаем тензор индексов узлов
            node_indices = torch.arange(num_nodes, dtype=torch.float32).unsqueeze(
                1
            )  # Добавляем дополнительное измерение

            # Добавляем индексы как признак узлов
            graph.ndata["features"] = node_indices

    def __getitem__(self, idx):
        return self.graphs[idx], self.labels[idx]

    def __len__(self):
        return len(self.graphs)


# Создаем экземпляр датасета
dataset = CustomGraphDataset()
# Проверка
print(f"Количество графов в датасете: {len(dataset)}")
graph, label = dataset[0]
print(f"Первый граф: {graph}")
print(f"Его метка: {label}")

num_examples = len(dataset)
num_train = int(num_examples * 0.8)

train_sampler = SubsetRandomSampler(torch.arange(num_train))
test_sampler = SubsetRandomSampler(torch.arange(num_train, num_examples))

# train_dataloader = DataLoader(dataset, batch_size=8, shuffle=True, collate_fn=dgl.batch)


class MLP(nn.Module):
    """Двухслойный MLP для использования в качестве агрегатора в GIN"""

    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.layers = nn.ModuleList()
        self.layers.append(nn.Linear(input_dim, hidden_dim))
        self.layers.append(nn.Linear(hidden_dim, output_dim))
        self.batch_norm = nn.BatchNorm1d(hidden_dim)

    def forward(self, x):
        x = F.relu(self.batch_norm(self.layers[0](x)))
        return self.layers[1](x)


class CustomGIN(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, num_layers=5, dropout=0.5):
        super().__init__()
        self.layers = nn.ModuleList()
        self.batch_norms = nn.ModuleList()

        for i in range(num_layers):
            if i == 0:
                mlp = MLP(input_dim, hidden_dim, hidden_dim)
            else:
                mlp = MLP(hidden_dim, hidden_dim, hidden_dim)

            self.layers.append(GINConv(mlp, learn_eps=True))
            self.batch_norms.append(nn.BatchNorm1d(hidden_dim))

        self.linear_prediction = nn.ModuleList()
        for i in range(num_layers + 1):
            if i == 0:
                self.linear_prediction.append(nn.Linear(input_dim, output_dim))
            else:
                self.linear_prediction.append(nn.Linear(hidden_dim, output_dim))

        self.dropout = nn.Dropout(dropout)
        self.pooling = SumPooling()

    def forward(self, g, features):
        h = features
        hidden_rep = [h]

        edge_weight = g.edata["weight"]  # Получаем веса рёбер из графа

        for i, layer in enumerate(self.layers):
            h = layer(g, h, edge_weight=edge_weight)  # Передаем edge_weight в GINConv
            h = self.batch_norms[i](h)
            h = F.relu(h)
            hidden_rep.append(h)

        score_over_layers = 0
        for i, h in enumerate(hidden_rep):
            pooled_h = self.pooling(g, h)
            score_over_layers += self.dropout(self.linear_prediction[i](pooled_h))

        return score_over_layers


def save_model(model, path="best_model.pth"):
    torch.save(model.state_dict(), path)
    print(f"Модель сохранена в {path}")


class EarlyStopping:
    def __init__(self, patience=5, delta=0, path="best_model.pth"):
        """
        Args:
            patience (int): Сколько эпох ждать, если нет улучшения
            delta (float): Минимальное изменение для улучшения
            path (str): Путь для сохранения лучшей модели
        """
        self.patience = patience
        self.delta = delta
        self.path = path
        self.best_score = None
        self.counter = 0
        self.early_stop = False
        self.best_val_acc = float("-inf")

    def __call__(self, val_acc, model):
        if self.best_score is None:
            self.best_score = val_acc
            save_model(model, str(self.counter) + self.path)
            self.best_val_acc = val_acc
        elif val_acc < self.best_score + self.delta:
            print(f"EarlyStopping counter: {self.counter} out of {self.patience}")
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            print(f"New best score: {val_acc}")
            self.best_score = val_acc
            save_model(model, str(self.counter) + self.path)
            self.best_val_acc = val_acc
            self.counter = 0


def evaluate(dataloader, device, model):
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for batched_graph, labels in dataloader:
            batched_graph = batched_graph.to(device)
            labels = labels.to(device)
            features = batched_graph.ndata["features"].float()
            batched_graph.edata["weight"] = batched_graph.edata["weight"].float()
            outputs = model(batched_graph, features)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    return correct / total


def train_model(train_loader, val_loader, device, model, num_epochs=100):
    sys.stdout = open("training_log.txt", "w")
    loss_function = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.005, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    early_stopping = EarlyStopping(
        patience=8, delta=0.002, path="best_model.pth"
    )  # Инициализируем early stopping

    for epoch in tqdm(range(num_epochs)):
        model.train()
        total_loss = 0

        for batched_graph, labels in tqdm(train_loader):
            batched_graph = batched_graph.to(device)
            labels = labels.to(device)

            features = batched_graph.ndata["features"].float()
            batched_graph.edata["weight"] = batched_graph.edata["weight"].float()

            optimizer.zero_grad()
            predictions = model(batched_graph, features)
            loss = loss_function(predictions, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print("Epoch done, step on the scheduler ...", end="")
        scheduler.step()
        print("evaluating ... ", end="")

        # Периодически проверяем точность на обучающем и валидационном датасетах
        val_acc = evaluate(val_loader, device, model)
        print(
            f"Epoch {epoch + 1}/{num_epochs}, Loss: {total_loss:.4f}, Val Accuracy: {val_acc:.4f}"
        )
        early_stopping(val_acc, model)
        if early_stopping.early_stop:
            print("Early stopping")
            break

    print(
        f"Training finished! Best validation accuracy: {early_stopping.best_val_acc:.4f}"
    )
    dist.destroy_process_group()


def get_dataloaders(dataset, seed, batch_size=1):
    train_set, val_set, test_set = split_dataset(
        dataset, frac_list=[0.8, 0.1, 0.1], shuffle=True, random_state=seed
    )
    train_loader = GraphDataLoader(
        train_set, use_ddp=True, batch_size=batch_size, shuffle=True
    )
    val_loader = GraphDataLoader(val_set, batch_size=batch_size)
    test_loader = GraphDataLoader(test_set, batch_size=batch_size)

    return train_loader, val_loader, test_loader


# ############################
# # Проверка уникальных значений меток в тренировочном и тестовом датасетах
# train_labels = []
# test_labels = []

# # Собираем все метки из train_dataloader
# for _, labels in train_dataloader:
#     train_labels.extend(labels.tolist())

# # Собираем все метки из test_dataloader
# for _, labels in test_dataloader:
#     test_labels.extend(labels.tolist())

# # Выводим уникальные значения меток
# train_labels = torch.tensor(train_labels)
# test_labels = torch.tensor(test_labels)

# print(f"Уникальные метки в тренировочном датасете: {train_labels.unique()}")
# print(f"Уникальные метки в тестовом датасете: {test_labels.unique()}")

# ############################

init_process_group(world_size=1, rank=0)
print("Process group initialized")
train_dataloader, test_dataloader, val_dataloader = get_dataloaders(
    dataset, seed=99, batch_size=1
)
print("Data loaded")
# Размер входных признаков графа, количество скрытых нейронов, количество классов
input_dim = 1  # Мы используем веса рёбер в качестве признаков
hidden_dim = 128  # Количество скрытых нейронов, можно настраивать
output_dim = 7  # 7 классов для задачи классификации
num_layers = 12  # Количество слоёв GIN
device = "cuda"
num_epochs = 100
dropout = 0.7


# Создаём модель
def init_model(seed, device, input_dim, output_dim, hidden_dim, dropout):
    torch.manual_seed(seed)
    model = CustomGIN(
        input_dim, hidden_dim=hidden_dim, output_dim=output_dim, dropout=dropout
    ).to(device)

    if device != "cpu":
        model = DataParallel(model, device_ids=[device], output_device=device)
    else:
        model = DistributedDataParallel(model)

    return model


model = init_model(
    seed=42,
    device=device,
    input_dim=input_dim,
    hidden_dim=hidden_dim,
    output_dim=output_dim,
    dropout=dropout,
)

device = torch.device("cuda:0")
print(dgl.backend.backend_name)  # Должно быть pytorch c версией cuda (иначе cpu версия)
print("Is cuda", next(model.parameters()).is_cuda)

train_model(
    train_dataloader,
    test_dataloader,
    device,
    model,
    num_epochs,
)
