document.addEventListener("DOMContentLoaded", () => {
    const chartDataDiv = document.getElementById("chart-data");

    const visitsChartData = JSON.parse(chartDataDiv.dataset.visits);
    const visitsChartLabels = JSON.parse(chartDataDiv.dataset.visitsLabels);
    let activityChartData = JSON.parse(chartDataDiv.dataset.activity);
    const activityChartLabels = JSON.parse(chartDataDiv.dataset.activityLabels);

    // Ensure numbers are integers
    activityChartData = activityChartData.map(x => Math.floor(x));

    // Visits chart
    new Chart(document.getElementById("visitsChart"), {
        type: "bar",
        data: {
            labels: visitsChartLabels,
            datasets: [{
                label: "Visit Count",
                data: visitsChartData,
                backgroundColor: "rgba(54, 162, 235, 0.7)"
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: true, text: "Visits per Site" }
            }
        }
    });

    // Activity chart
    new Chart(document.getElementById("activityChart"), {
        type: "line",
        data: {
            labels: activityChartLabels,
            datasets: [{
                label: "Submissions",
                data: activityChartData,
                borderColor: "rgba(255, 99, 132, 1)",
                backgroundColor: "rgba(255, 99, 132, 0.2)",
                tension: 0.3,
                fill: true,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: true, text: "Mentee Submissions (Last 7 Days)" }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
});
