let isDetectionRunning = true

document.getElementById('toggle-detection').addEventListener('click', () => {
    isDetectionRunning = !isDetectionRunning

    const button = document.getElementById('toggle-detection')
    button.innerText = isDetectionRunning ? 'Stop Detection' : 'Start Detection'

    fetch('/toggle-detection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ isDetectionRunning })
    }).catch(error => console.error('Error toggling detection:', error))
})

setInterval(async () => {
    try {
        const response = await fetch('/data')
        if (response.ok) {
            const data = await response.json()
            document.getElementById('status').innerText = data.status
            document.getElementById('captured-image').src = data.image + `?t=${new Date().getTime()}`
            document.getElementById('license-plate').innerText = data.license_plate

            // Update Plate Status
            const plateStatusElement = document.getElementById('plate-status')
            if (data.plate_known) {
                plateStatusElement.innerText = "Known"
                plateStatusElement.style.color = "green"
            } else if (data.license_plate) { // Ensure that there's a plate detected
                plateStatusElement.innerText = "Unknown"
                plateStatusElement.style.color = "red"
            } else {
                plateStatusElement.innerText = "N/A"
                plateStatusElement.style.color = "yellow"
            }

            // Update Gate Status
            const gateStatusElement = document.getElementById('gate-status')
            gateStatusElement.innerText = data.gate_status

            // Optionally, change color based on gate status
            switch (data.gate_status) {
                case "Gate Opening":
                case "Gate Closing":
                    gateStatusElement.style.color = "orange"
                    break
                case "Gate Opened":
                case "Gate Closed":
                    gateStatusElement.style.color = "green"
                    break
                case "Gate Closed - Unknown Plate":
                    gateStatusElement.style.color = "red"
                    break
                default:
                    gateStatusElement.style.color = "yellow"
            }
        }
    } catch (error) {
        console.error('Error fetching data:', error)
    }
}, 2000)
