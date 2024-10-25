document.addEventListener("DOMContentLoaded", () => {
    const socket = new WebSocket("ws://localhost:8000/ws");

    socket.onopen = () => {
        console.log('WebSocket connection established');
        document.getElementById("status").textContent = 'Connected to server';
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.status_update) {
            document.getElementById("status").textContent = data.status_update;
        } else if (data.text) {
            const li = document.createElement("li");
            li.textContent = data.text;
            document.getElementById("transcriptions").appendChild(li);

            // Scroll to the bottom of the transcriptions
            const transcriptionsContainer = document.getElementById("transcriptions");
            transcriptionsContainer.scrollTop = transcriptionsContainer.scrollHeight;
        } else if (data.error) {
            console.error('Transcription error:', data.error);
        }
    };

    socket.onclose = () => {
        console.log('WebSocket connection closed');
        document.getElementById("status").textContent = 'Disconnected from server';
    };

    socket.onerror = (error) => {
        console.log('WebSocket error:', error);
    };

    document.getElementById("start").addEventListener("click", () => {
        $('#chunkTimeModal').modal('show');
    });

    document.getElementById("confirmChunkTime").addEventListener("click", () => {
        const chunkTime = document.getElementById("chunkTimeInput").value;
        const language = document.getElementById("languageSelect").value;
        socket.send(JSON.stringify({ action: 'start', chunk_time: parseFloat(chunkTime), language: language }));
        $('#chunkTimeModal').modal('hide');
    });

    document.getElementById("stop").addEventListener("click", () => {
        socket.send(JSON.stringify({ action: 'stop' }));
    });

    document.getElementById("clear").addEventListener("click", () => {
        document.getElementById("transcriptions").innerHTML = "";
    });

    document.getElementById("save").addEventListener("click", () => {
        const transcriptionsContainer = document.getElementById("transcriptions");
        let textContent = "";

        // Collect all transcriptions into a single string
        transcriptionsContainer.querySelectorAll("li").forEach(item => {
            textContent += item.textContent + "\n";
        });

        // Create a blob from the text content
        const blob = new Blob([textContent], { type: "text/plain" });
        const url = URL.createObjectURL(blob);

        // Create a link and trigger the download
        const a = document.createElement("a");
        a.href = url;
        a.download = "transcriptions.txt";
        document.body.appendChild(a);
        a.click();

        // Clean up
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
});