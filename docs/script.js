function copyCode(button) {
    const codeBlock = button.parentElement.querySelector('code');
    const text = codeBlock.textContent;
    navigator.clipboard.writeText(text)
        .then(() => {
            button.textContent = 'Скопировано!';
            setTimeout(() => {
                button.textContent = 'Копировать';
            }, 2000);
        })
        .catch(err => {
            console.error('Ошибка копирования:', err);
        });
}