// Retrieve a cookie value by its name
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Submit an edited post
function submitrequest(id) {
    const textareaValue = document.getElementById(`textarea_${id}`).value;
    fetch(`/edit/${id}`, {
        method: "POST",
        headers: { "Content-type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
        body: JSON.stringify({ content: textareaValue })
    })
    .then(response => {
        if (!response.ok) throw new Error("Network response not ok");
        return response.json();
    })
    .then(result => {
        document.getElementById(`content_${id}`).innerText = result.data;
        $(`#modal_edit_post_${id}`).modal('hide');
    })
    .catch(error => {
        console.log("Fetch error:", error.message);
    });
    
    document.querySelector(`[data-target="#modal_edit_post_${id}"]`).blur();
}

// Toggle a post's like status
function like_trigger(id, who_liked) {
    const btn = document.getElementById(`${id}`);
    btn.disabled = true;
    let endpoint = `/toggle_like/${id}`;
    let newBtnContent, newBtnClass, oldBtnClass;

    if (who_liked.includes(id)) {
        newBtnContent = '<i class="fa fa-thumbs-up"></i> Like';
        newBtnClass = 'btn-up';
        oldBtnClass = 'btn-down';
    } else {
        newBtnContent = '<i class="fa fa-thumbs-down"></i> Dislike';
        newBtnClass = 'btn-down';
        oldBtnClass = 'btn-up';
    }


    fetch(endpoint, {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") }
    })
    .then(response => response.json())
    .then(data => {
        // Basándonos en la respuesta del servidor:
        if (data.liked) {
            btn.classList.replace('btn-up', 'btn-down');
            btn.innerHTML = '<i class="fa fa-thumbs-down"></i> Dislike';
            who_liked.push(id);
        } else {
            btn.classList.replace('btn-down', 'btn-up');
            btn.innerHTML = '<i class="fa fa-thumbs-up"></i> Like';
            const index = who_liked.indexOf(id);
            if (index > -1) who_liked.splice(index, 1);
        }
    
        const likesCountElement = document.getElementById(`like-count-${id}`);
        if (likesCountElement) {
            likesCountElement.innerText = data.total_likes;
        }
    
        btn.disabled = false;
    })
    .catch(error => {
        console.error("Error:", error);
        btn.disabled = false;
    });
    
}
