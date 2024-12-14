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
            document.getElementById('captured-image').src = data.image
            document.getElementById('license-plate').innerText = data.license_plate
        }
    } catch (error) {
        console.error('Error fetching data:', error)
    }
}, 2000)