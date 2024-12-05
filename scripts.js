document.getElementById('code-here-button').addEventListener('click', function() {
    const hwidElement = document.getElementById('hwid');
    if (!hwidElement.textContent) {
        alert('Bạn cần phải vượt qua link để nhận được HWID trước!');
    } else {
        alert('Chúc mừng! Bạn đã vượt qua link.');
        // You can add more actions here
    }
});

// Generate API Key
document.getElementById('generate-key-button').addEventListener('click', function() {
    const key = 'RinKey-' + Math.random().toString(36).substring(2, 10);
    document.getElementById('api-key').textContent = `Your API key is: ${key}`;
});

// Lấy HWID từ tham số URL và hiển thị
const urlParams = new URLSearchParams(window.location.search);
const hwid = urlParams.get('hwid');
if (hwid) {
    document.getElementById('hwid').textContent = hwid;
}