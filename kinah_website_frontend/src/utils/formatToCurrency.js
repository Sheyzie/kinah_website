export function formatToCurrency(amount) {
    const formatted = new Intl.NumberFormat('en-NG', {
        style: 'currency',
        currency: 'NGN',
    }).format(amount);

    return formatted
}