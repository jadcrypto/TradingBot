const ws = new WebSocket("ws://127.0.0.1:8000/ws");

ws.onopen = () => {
    console.log("WebSocket connection established.");
    document.getElementById("loading").textContent = "Loading data...";
};

ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    console.log("Received data from the Python server...");

    const tbody = document.getElementById("crypto-data");
    const errorDiv = document.getElementById("error");
    const loadingDiv = document.getElementById("loading");

    // Clear previous data and errors
    tbody.innerHTML = "";
    errorDiv.textContent = "";
    loadingDiv.textContent = "";

    if (response.error) {
        errorDiv.textContent = `Error: ${response.error}`;
        return;
    }

    // Populate cryptocurrency data
    response.results.forEach((item) => {
        const row = document.createElement("tr");

        const symbolCell = document.createElement("td");
        symbolCell.textContent = item.symbol;
        row.appendChild(symbolCell);

        const signalCell = document.createElement("td");
        signalCell.textContent = item.signal;
        row.appendChild(signalCell);

        const percentageCell = document.createElement("td");
        percentageCell.textContent = `${item.percentage.toFixed(2)}%`;
        row.appendChild(percentageCell);

        const priceCell = document.createElement("td");
        priceCell.textContent = item.price ? `$${item.price.toFixed(2)}` : "N/A";
        row.appendChild(priceCell);

        const timeframesCell = document.createElement("td");
        timeframesCell.textContent = item.timeframes.join(", ");
        row.appendChild(timeframesCell);

        tbody.appendChild(row);
    });

    console.log("Data displayed in the HTML page.");

    // Example chart data
    const labels = response.results.map(item => item.symbol);
    const data = response.results.map(item => item.percentage);

    const ctx = document.getElementById('cryptoChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Percentage',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
};

ws.onclose = () => {
    console.error("WebSocket connection closed. Retrying...");
    document.getElementById("error").textContent = "Connection closed. Retrying...";
    setTimeout(() => {
        location.reload(); // Reload the page to reconnect
    }, 5000);
};

ws.onerror = (error) => {
    console.error("WebSocket error:", error);
    document.getElementById("error").textContent = "An error occurred with the WebSocket connection.";
};
