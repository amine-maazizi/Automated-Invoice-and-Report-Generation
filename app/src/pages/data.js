function initializeDataPage() {
    console.log("Data page initialized");

    const fileInput = document.getElementById('file-input');
    const loadDataBtn = document.getElementById('load-data-btn');
    const dataTable = document.getElementById('data-table');

    loadDataBtn.addEventListener('click', () => {
        if (fileInput.files.length === 0) {
            alert('Please select a file first.');
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);  // Ensure the key 'file' matches what Flask expects

        fetch('http://localhost:5000/upload-excel', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
                console.error('Error from server:', data.error);
                return;
            }

            renderTable(data.data);
        })
        .catch(error => {
            console.error('Error uploading file:', error);
            alert('Failed to upload file. Please check the console for more details.');
        });
    });

    function renderTable(data) {
        dataTable.innerHTML = ''; // Clear existing content

        if (data.length === 0) {
            dataTable.innerHTML = '<tr><td>No data available</td></tr>';
            return;
        }

        const headers = Object.keys(data[0]);
        const headerRow = document.createElement('tr');

        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            headerRow.appendChild(th);
        });

        dataTable.appendChild(headerRow);

        data.forEach(row => {
            const rowElement = document.createElement('tr');
            headers.forEach(header => {
                const td = document.createElement('td');
                td.textContent = row[header];
                rowElement.appendChild(td);
            });
            dataTable.appendChild(rowElement);
        });
    }
}

module.exports = { initializeDataPage };
