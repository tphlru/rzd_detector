const xValuesEF = ["Спокойствие","Радость","Грусть","Злость"];
const yValuesEF = [60,10,8,2];
const barColors = ["black", "orange","blue","red","brown"];

const xValuesEV = ["Спокойствие","Радость","Грусть","Злость"];
const yValuesEV = [50,15,11,1];
new Chart("emotions", {
	type: "pie",
	data: {
		labels: xValuesEV,
		datasets: [{
			backgroundColor: barColors,
			data: yValuesEV
		}]
	},
	options: {}
});

const xValuesVzdoh = [16,14,12,10,8,6,4,2,0];
const yValuesVzdoh = [73,75,69,83,85,98,111,115,110];
new Chart("vzdoh", {
	type: "line",
	data: {
		labels: xValuesVzdoh,
		datasets: [{
			backgroundColor:"rgba(0,255,0,0.4)",
			borderColor: "rgba(0,255,0,0.5)",
			data: yValuesVzdoh,
			fill: true,
		}]
	},
});

const xValuesPulse = [16,14,12,10,8,6,4,2,0];
const yValuesPulse = [73,75,69,83,85,98,111,115,110];
new Chart("pulse", {
	type: "line",
	data: {
		labels: xValuesPulse,
		datasets: [{
			backgroundColor:"rgba(255,0,0,1.0)",
			borderColor: "rgba(255,0,0,0.1)",
			data: yValuesPulse,
		}]
	},
});
		
const xValuesMorganie = [16,14,12,10,8,6,4,2,0];
const yValuesMorganie = [200,200,88,83,85,20,111,115,110];
new Chart("morganie", {
	type: "line",
	data: {
		labels: xValuesMorganie,
		datasets: [{
			backgroundColor:"rgba(0,0,255,0.2)",
			borderColor: "rgba(0,0,255,0.1)",
			data: yValuesMorganie,
			fill: true,
		},
	{
			backgroundColor:"rgba(0,255,0,0.2)",
			borderColor: "rgba(0,255,0,0.1)",
			data: yValuesVzdoh,
			fill: true,
		}]
	}
});