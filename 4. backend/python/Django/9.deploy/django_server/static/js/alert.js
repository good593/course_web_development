window.addEventListener('DOMContentLoaded', () => {
	const messages = document.querySelectorAll('.django-message');

	messages.forEach((msg) => {
		const tag = msg.dataset.tag;
		const text = msg.textContent.trim();

		if (tag === 'success') {
			Swal.fire({
				icon: 'success',
				title: 'Success!',
				text: text,
			});
		} else if (tag === 'error') {
			Swal.fire({
				icon: 'error',
				title: 'Error!',
				text: text,
			});
		} else if (tag === 'warning') {
			Swal.fire({
				icon: 'warning',
				title: 'Warning!',
				text: text,
			});
		} else {
			Swal.fire({
				icon: 'info',
				title: 'Notice',
				text: text,
			});
		}
	});
});
