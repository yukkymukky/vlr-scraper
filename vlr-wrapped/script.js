function renderData(data) {
    document.getElementById('username').textContent = data.username;
    document.getElementById('year').textContent = data.year;
    document.getElementById('total-posts').textContent = data.total_posts_this_year;
    document.getElementById('posts-caption').textContent = `That's about ${(data.total_posts_this_year / 12).toFixed(1)} posts per month!`;

    document.getElementById('net-votes').textContent = data.net_votes_this_year > 0 ? `+${data.net_votes_this_year}` : data.net_votes_this_year;
    document.getElementById('upvotes').textContent = data.upvotes_this_year;
    document.getElementById('downvotes').textContent = Math.abs(data.downvotes_this_year);

    const totalVotes = data.upvotes_this_year + Math.abs(data.downvotes_this_year);
    const upvotePercent = (data.upvotes_this_year / totalVotes) * 100;
    const downvotePercent = (Math.abs(data.downvotes_this_year) / totalVotes) * 100;

    document.getElementById('upvote-bar').style.setProperty('--width', `${upvotePercent}%`);
    document.getElementById('downvote-bar').style.setProperty('--width', `${downvotePercent}%`);

    document.getElementById('streak').textContent = `${data.longest_post_streak_days} DAYS`;
    const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    document.getElementById('active-month').textContent = monthNames[data.most_active_month - 1];

    const topPostsContainer = document.getElementById('top-posts');
    topPostsContainer.innerHTML = '';
    data.top_5_posts_by_interaction.forEach(post => {
        const postName = post.url.split('/').pop();
        const postElement = document.createElement('div');
        postElement.className = 'post-item';
        postElement.innerHTML = `
            <div class="post-url">${postName}</div>
            <div class="post-votes">
                ${post.upvotes > 0 ? `<span class="upvotes">+${post.upvotes}</span>` : ''}
                ${post.downvotes < 0 ? `<span class="downvotes">${post.downvotes}</span>` : ''}
            </div>
        `;
        topPostsContainer.appendChild(postElement);
    });

    const fansContainer = document.getElementById('fans-list');
    fansContainer.innerHTML = '';
    data.top_5_biggest_fans.forEach(fan => {
        const fanElement = document.createElement('div');
        fanElement.className = 'fan-item';
        fanElement.innerHTML = `
            <div class="fan-name">${fan.user}</div>
            <div class="fan-replies">${fan.replies}</div>
        `;
        fansContainer.appendChild(fanElement);
    });
}

function loadJSON(filename, callback) {
    fetch(filename)
        .then(response => response.json())
        .then(data => callback(data))
        .catch(err => alert('Failed to load JSON: ' + err));
}

// Control buttons
window.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const file = params.get('json');
    if (file) {
        loadJSON(file, renderData);
    }

    document.getElementById('load-sample').addEventListener('click', () => loadJSON('sample.json', renderData));

    document.getElementById('load-custom').addEventListener('click', () => {
        const jsonInput = document.getElementById('json-input');
        if (jsonInput.style.display === 'none' || jsonInput.style.display === '') {
            jsonInput.style.display = 'block';
        } else {
            try {
                const customData = JSON.parse(jsonInput.value);
                renderData(customData);
                jsonInput.style.display = 'none';
            } catch (error) {
                alert('Invalid JSON format. Please check your data.');
            }
        }
    });

    document.getElementById('save-image').addEventListener('click', () => {
        const card = document.getElementById('wrapped-card');
        const saveButton = document.getElementById('save-image');
        const originalText = saveButton.textContent;
        saveButton.textContent = 'Generating...';
        saveButton.disabled = true;

        setTimeout(() => {
            html2canvas(card, {
                scale: 2,
                backgroundColor: null,
                logging: false,
                useCORS: true,
                allowTaint: true,
                width: 1200,
                height: 630
            }).then(canvas => {
                const link = document.createElement('a');
                link.download = `vlrgg-wrapped-${document.getElementById('username').textContent}-${document.getElementById('year').textContent}.png`;
                link.href = canvas.toDataURL('image/png');
                link.click();
                saveButton.textContent = originalText;
                saveButton.disabled = false;
            }).catch(error => {
                console.error('Error generating image:', error);
                alert('There was an error generating the image. Please try again.');
                saveButton.textContent = originalText;
                saveButton.disabled = false;
            });
        }, 100);
    });
});
