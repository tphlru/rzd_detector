import dgl
import numpy as np
import tensorflow as tf
import torch
import tensorflow_datasets as tfds
from tqdm import tqdm

# Загрузка вашего датасета
loaded_dataset = tf.data.Dataset.load("docs/notebooks/faceemotions/dataset/")
df = tfds.as_dataframe(loaded_dataset)


def create_dgl_graph(adjacency, values, shape):
    # Создаем пустой DGLGraph
    graph = dgl.DGLGraph()

    # Добавляем узлы
    num_nodes = shape[0]
    graph.add_nodes(num_nodes)

    # Добавляем рёбра
    src, dst = np.array(adjacency).T
    graph.add_edges(src, dst)

    # Добавляем веса рёбер
    graph.edata["weight"] = torch.tensor(values, dtype=torch.float32)

    return graph


# Преобразование каждого элемента датасета в DGL граф
graphs = []
labels = []

for _, row in tqdm(df.iterrows(), total=len(df)):
    adj = row["adjacency"]
    values = row["values"]
    shape = row["shape"]
    label = row["label"]

    graph = create_dgl_graph(adj, values, shape)
    graphs.append(graph)
    labels.append(label)

# Преобразование меток в тензор PyTorch
labels = torch.tensor(labels, dtype=torch.long)

# Сохраняем графы и метки
graph_path = "saved_graphs.dgl"
label_path = "saved_labels.pt"

# Сохраняем графы
dgl.save_graphs(graph_path, graphs)

# Сохраняем метки
torch.save(labels, label_path)
