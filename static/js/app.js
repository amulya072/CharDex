/**
 * The College Underground - Unofficial Campus Network
 * Master Frontend Controller (Everything is Editable)
 */

// Web Audio API Synthesizer for Classic Poke & Interaction Sounds
class SoundEffects {
    constructor() {
        this.ctx = null;
    }

    init() {
        if (!this.ctx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                this.ctx = new AudioContext();
            }
        }
    }

    playPokeSound() {
        try {
            this.init();
            if (!this.ctx) return;
            if (this.ctx.state === 'suspended') {
                this.ctx.resume();
            }
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = 'triangle';
            
            const now = this.ctx.currentTime;
            osc.frequency.setValueAtTime(520, now);
            osc.frequency.exponentialRampToValueAtTime(780, now + 0.12);

            gain.gain.setValueAtTime(0.3, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now);
            osc.stop(now + 0.25);
        } catch (e) {
            console.warn('Audio effect unavailable', e);
        }
    }

    playClickSound() {
        try {
            this.init();
            if (!this.ctx) return;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = 'sine';
            const now = this.ctx.currentTime;
            osc.frequency.setValueAtTime(800, now);
            gain.gain.setValueAtTime(0.15, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(now);
            osc.stop(now + 0.08);
        } catch (e) {}
    }
}

const sfx = new SoundEffects();

// Toast Notification Manager
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast';
    
    let icon = '👉';
    if (type === 'success') icon = '✅';
    if (type === 'heart') icon = '❤️';
    if (type === 'vote') icon = '🗳️';
    if (type === 'event') icon = '📅';
    if (type === 'edit') icon = '✏️';
    if (type === 'error') icon = '⚠️';

    toast.innerHTML = `<span class="text-base">${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 400);
    }, 3500);
}

// ==================== THEME MANAGEMENT ====================

function initTheme() {
    const savedTheme = localStorage.getItem('college_theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    sfx.playClickSound();
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('college_theme', next);
    updateThemeIcon(next);
    showToast(`Switched to ${next === 'dark' ? 'Quad Dark Mode' : 'Classic 2004 TheFacebook Blue'}`, 'info');
}

function updateThemeIcon(theme) {
    const btn = document.getElementById('theme-toggle-btn');
    if (btn) {
        btn.innerHTML = theme === 'dark' ? '<i class="fas fa-sun text-amber-300"></i>' : '<i class="fas fa-moon"></i>';
    }
}

// ==================== INSTAGRAM STORIES PLAYER ====================

let storyTimer = null;
function playStory(title, imageUrl, authorName, authorAvatar, caption) {
    sfx.playClickSound();
    const modal = document.getElementById('story-player-modal');
    if (!modal) return;

    document.getElementById('story-title').textContent = title;
    document.getElementById('story-image').src = imageUrl;
    document.getElementById('story-author-name').textContent = authorName;
    document.getElementById('story-author-avatar').src = authorAvatar;
    document.getElementById('story-caption').textContent = caption;

    const bar = document.getElementById('story-progress-bar');
    bar.style.width = '0%';

    openModal('story-player-modal');

    // Smoothly animate progress bar over 4.5s
    clearTimeout(storyTimer);
    let start = Date.now();
    const duration = 4500;

    function frame() {
        const elapsed = Date.now() - start;
        const pct = Math.min(100, (elapsed / duration) * 100);
        bar.style.width = `${pct}%`;
        if (pct < 100 && modal.classList.contains('flex')) {
            requestAnimationFrame(frame);
        } else if (pct >= 100) {
            closeStoryPlayer();
        }
    }
    requestAnimationFrame(frame);
}

function closeStoryPlayer() {
    closeModal('story-player-modal');
    clearTimeout(storyTimer);
}

// ==================== INSTAGRAM PHOTO LIGHTBOX ====================

function openPhotoLightbox(postId, imageUrl, caption, likes, authorName, authorAvatar, authorHandle) {
    sfx.playClickSound();
    document.getElementById('lightbox-img').src = imageUrl;
    document.getElementById('lightbox-caption').textContent = caption;
    document.getElementById('lightbox-likes').textContent = `${likes} campus likes`;
    document.getElementById('lightbox-author').textContent = authorName;
    document.getElementById('lightbox-avatar').src = authorAvatar;
    document.getElementById('lightbox-handle').textContent = `@${authorHandle}`;

    openModal('photo-lightbox-modal');
}

// ==================== STUDENT CRUD (EVERYTHING EDITABLE) ====================

async function handleSaveStudent(event, studentId, form) {
    event.preventDefault();
    sfx.playClickSound();

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Parse badges into array
    if (data.badges) {
        data.badges = data.badges.split(',').map(b => b.trim()).filter(b => b.length > 0);
    }

    try {
        const res = await fetch(`/api/edit-student/${studentId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const resData = await res.json();
        if (resData.success) {
            showToast('Student profile updated successfully!', 'success');
            setTimeout(() => window.location.reload(), 600);
        } else {
            showToast(resData.error || 'Update failed', 'error');
        }
    } catch (e) {
        showToast('Error saving profile changes', 'error');
    }
}

async function handleCreateStudent(event, form) {
    event.preventDefault();
    sfx.playClickSound();

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
        const res = await fetch('/api/create-student', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const resData = await res.json();
        if (resData.success) {
            showToast('Student added to campus directory!', 'success');
            setTimeout(() => window.location.href = `/profile/${resData.id}`, 600);
        } else {
            showToast(resData.error || 'Creation failed', 'error');
        }
    } catch (e) {
        showToast('Error creating student', 'error');
    }
}

async function handleDeleteStudent(studentId) {
    if (!confirm("Are you sure you want to delete this student from the campus network?")) return;
    sfx.playClickSound();

    try {
        const res = await fetch(`/api/delete-student/${studentId}`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            showToast('Student removed from network', 'info');
            setTimeout(() => window.location.href = '/directory', 600);
        }
    } catch (e) {
        showToast('Error deleting student', 'error');
    }
}

// ==================== POSTS & COMMENTS CRUD ====================

function openEditPostModal(postId, content, imageUrl, tags) {
    document.getElementById('edit-post-id').value = postId;
    document.getElementById('edit-post-content').value = content;
    document.getElementById('edit-post-image').value = imageUrl;
    document.getElementById('edit-post-tags').value = tags;
    openModal('edit-post-modal');
}

async function handleSavePost(event) {
    event.preventDefault();
    sfx.playClickSound();

    const postId = document.getElementById('edit-post-id').value;
    const content = document.getElementById('edit-post-content').value;
    const imageUrl = document.getElementById('edit-post-image').value;
    const tags = document.getElementById('edit-post-tags').value;

    try {
        const res = await fetch(`/api/edit-post/${postId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content, image_url: imageUrl, tags })
        });
        const data = await res.json();
        if (data.success) {
            showToast('Post updated on the wire!', 'edit');
            closeModal('edit-post-modal');
            const postCard = document.getElementById(`post-card-${postId}`);
            if (postCard) {
                const contentText = postCard.querySelector('.post-content-text');
                if (contentText) contentText.textContent = content;
            }
        }
    } catch (e) {
        showToast('Error updating post', 'error');
    }
}

async function handleDeletePost(postId) {
    if (!confirm("Delete this post from the campus wire?")) return;
    sfx.playClickSound();

    try {
        const res = await fetch(`/api/delete-post/${postId}`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            showToast('Post deleted', 'info');
            const card = document.getElementById(`post-card-${postId}`);
            if (card) {
                card.style.transition = 'opacity 0.3s, transform 0.3s';
                card.style.opacity = '0';
                card.style.transform = 'scale(0.95)';
                setTimeout(() => card.remove(), 300);
            }
        }
    } catch (e) {
        showToast('Error deleting post', 'error');
    }
}

async function handleDeleteComment(commentId) {
    if (!confirm("Delete this comment?")) return;
    sfx.playClickSound();

    try {
        const res = await fetch(`/api/delete-comment/${commentId}`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            showToast('Comment deleted', 'info');
            const item = document.getElementById(`comment-item-${commentId}`);
            if (item) item.remove();
        }
    } catch (e) {
        showToast('Error deleting comment', 'error');
    }
}

// ==================== POLLS CRUD ====================

function openEditPollModal(pollId, question, category) {
    document.getElementById('edit-poll-id').value = pollId;
    document.getElementById('edit-poll-question').value = question;
    document.getElementById('edit-poll-category').value = category;
    openModal('edit-poll-modal');
}

async function handleSavePoll(event) {
    event.preventDefault();
    sfx.playClickSound();

    const pollId = document.getElementById('edit-poll-id').value;
    const question = document.getElementById('edit-poll-question').value;
    const category = document.getElementById('edit-poll-category').value;

    try {
        const res = await fetch(`/api/edit-poll/${pollId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, category })
        });
        const data = await res.json();
        if (data.success) {
            showToast('Poll updated!', 'edit');
            closeModal('edit-poll-modal');
            const card = document.getElementById(`poll-card-${pollId}`);
            if (card) {
                const qText = card.querySelector('.poll-question-text');
                if (qText) qText.textContent = question;
            }
        }
    } catch (e) {
        showToast('Error updating poll', 'error');
    }
}

async function handleDeletePoll(pollId) {
    if (!confirm("Delete this campus poll?")) return;
    sfx.playClickSound();

    try {
        const res = await fetch(`/api/delete-poll/${pollId}`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            showToast('Poll deleted', 'info');
            const card = document.getElementById(`poll-card-${pollId}`);
            if (card) card.remove();
        }
    } catch (e) {
        showToast('Error deleting poll', 'error');
    }
}

// ==================== EVENTS CRUD ====================

function openEditEventModal(eventId, title, desc, cat, dateStr, loc, img) {
    document.getElementById('edit-event-id').value = eventId;
    document.getElementById('edit-event-title').value = title;
    document.getElementById('edit-event-desc').value = desc;
    document.getElementById('edit-event-cat').value = cat;
    document.getElementById('edit-event-date').value = dateStr;
    document.getElementById('edit-event-loc').value = loc;
    document.getElementById('edit-event-img').value = img;
    openModal('edit-event-modal');
}

async function handleSaveEvent(event) {
    event.preventDefault();
    sfx.playClickSound();

    const eventId = document.getElementById('edit-event-id').value;
    const title = document.getElementById('edit-event-title').value;
    const description = document.getElementById('edit-event-desc').value;
    const category = document.getElementById('edit-event-cat').value;
    const date_str = document.getElementById('edit-event-date').value;
    const location = document.getElementById('edit-event-loc').value;
    const image_url = document.getElementById('edit-event-img').value;

    try {
        const res = await fetch(`/api/edit-event/${eventId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, category, date_str, location, image_url })
        });
        const data = await res.json();
        if (data.success) {
            showToast('Event updated!', 'edit');
            closeModal('edit-event-modal');
            setTimeout(() => window.location.reload(), 400);
        }
    } catch (e) {
        showToast('Error updating event', 'error');
    }
}

async function handleDeleteEvent(eventId) {
    if (!confirm("Delete this campus event?")) return;
    sfx.playClickSound();

    try {
        const res = await fetch(`/api/delete-event/${eventId}`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            showToast('Event removed', 'info');
            const card = document.getElementById(`event-card-${eventId}`);
            if (card) card.remove();
        }
    } catch (e) {
        showToast('Error deleting event', 'error');
    }
}

// ==================== CAMPUS MESSENGER (DMs) ====================

async function handleSendMessage(event, targetId, form) {
    event.preventDefault();
    sfx.playClickSound();
    const input = document.getElementById('chat-input');
    const content = input.value.trim();
    if (!content) return;

    try {
        const res = await fetch('/api/send-message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ receiver_id: parseInt(targetId), content: content })
        });
        const data = await res.json();
        if (data.success) {
            input.value = '';
            const container = document.getElementById('messages-container');
            if (container) {
                const bubble = document.createElement('div');
                bubble.className = 'flex justify-end';
                bubble.innerHTML = `
                    <div class="flex items-end gap-2 max-w-[75%] flex-row-reverse">
                        <img src="${data.message.sender_avatar}" class="w-6 h-6 rounded-full object-cover mb-1 border border-gray-200">
                        <div class="bg-blue-600 text-white rounded-t-2xl rounded-bl-2xl rounded-br-xs px-3.5 py-2 text-xs shadow-xs">
                            <p class="leading-relaxed">${data.message.content}</p>
                            <span class="block text-[9px] mt-1 text-blue-200 text-right">Just now</span>
                        </div>
                    </div>
                `;
                container.appendChild(bubble);
                container.scrollTop = container.scrollHeight;
            }
        }
    } catch (e) {
        showToast('Failed to send message', 'error');
    }
}

// ==================== CONFESSIONS ====================

async function handleUpvoteConfession(confId, btn) {
    sfx.playPokeSound();
    try {
        const res = await fetch('/api/upvote-confession', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ confession_id: parseInt(confId) })
        });
        const data = await res.json();
        if (data.success) {
            const countElem = document.getElementById(`confession-votes-${confId}`);
            if (countElem) countElem.textContent = data.upvotes;
            btn.classList.add('text-blue-700', 'bg-blue-100');
        }
    } catch (e) {}
}

async function handleDeleteConfession(confId) {
    if (!confirm("Delete this confession?")) return;
    try {
        const res = await fetch(`/api/delete-confession/${confId}`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            const card = document.getElementById(`confession-card-${confId}`);
            if (card) card.remove();
            showToast('Confession deleted', 'info');
        }
    } catch (e) {}
}

// ==================== CORE SOCIAL INTERACTIONS ====================

async function pokeStudent(targetId, targetName, btnElement) {
    sfx.playPokeSound();
    if (btnElement) {
        btnElement.classList.add('animating');
        setTimeout(() => btnElement.classList.remove('animating'), 500);
    }

    try {
        const res = await fetch('/api/poke', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target_id: targetId })
        });
        const data = await res.json();
        if (data.success) {
            showToast(data.message, 'info');
            const pokeCountElem = document.getElementById(`poke-count-${targetId}`);
            if (pokeCountElem) {
                pokeCountElem.textContent = `${data.poke_count} pokes`;
            }
        } else {
            showToast(data.error || 'Failed to poke', 'error');
        }
    } catch (err) {
        showToast('Network error while poking', 'error');
    }
}

async function handleFriendAction(targetId, action, btnElement) {
    sfx.playClickSound();
    try {
        const res = await fetch('/api/friend-action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target_id: targetId, action: action })
        });
        const data = await res.json();
        if (data.success) {
            if (action === 'send') {
                showToast('Friend request sent!', 'success');
                if (btnElement) {
                    btnElement.innerHTML = '<i class="fas fa-clock mr-1.5"></i> Requested';
                    btnElement.className = 'px-3 py-1.5 bg-gray-200 text-gray-700 text-xs font-semibold rounded border border-gray-300';
                    btnElement.onclick = () => handleFriendAction(targetId, 'remove', btnElement);
                }
            } else if (action === 'accept') {
                showToast('Friend request accepted! You are now friends.', 'success');
                setTimeout(() => window.location.reload(), 500);
            } else if (action === 'decline' || action === 'remove') {
                showToast('Friend connection updated.', 'info');
                setTimeout(() => window.location.reload(), 400);
            }
        } else {
            showToast(data.error || 'Action failed', 'error');
        }
    } catch (err) {
        showToast('Error updating friendship', 'error');
    }
}

async function handleFollowAction(targetId, btnElement) {
    sfx.playClickSound();
    try {
        const res = await fetch('/api/follow-action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target_id: targetId })
        });
        const data = await res.json();
        if (data.success) {
            if (data.is_following) {
                showToast('Now following!', 'success');
                btnElement.innerHTML = '<i class="fas fa-check mr-1.5"></i> Following';
                btnElement.className = 'px-4 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-800 text-xs font-bold rounded transition border border-gray-300';
            } else {
                showToast('Unfollowed', 'info');
                btnElement.innerHTML = '<i class="fas fa-plus mr-1.5"></i> Follow';
                btnElement.className = 'px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded transition shadow-sm';
            }
            const countElem = document.getElementById(`followers-count-${targetId}`);
            if (countElem) {
                countElem.textContent = data.followers_count;
            }
        }
    } catch (err) {
        showToast('Error following student', 'error');
    }
}

async function submitVote(pollId, optionIndex) {
    sfx.playClickSound();
    try {
        const res = await fetch('/api/vote-poll', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ poll_id: pollId, option_index: optionIndex })
        });
        const data = await res.json();
        if (data.success) {
            showToast('Vote counted on campus wire! (+2 Karma)', 'vote');
            const pollContainer = document.getElementById(`poll-card-${pollId}`);
            if (pollContainer) {
                const totalElem = pollContainer.querySelector('.poll-total-votes');
                if (totalElem) totalElem.textContent = `${data.total_votes} votes`;

                data.options_data.forEach(opt => {
                    const row = pollContainer.querySelector(`.poll-opt-${opt.index}`);
                    if (row) {
                        const bar = row.querySelector('.poll-progress-bar');
                        const pctText = row.querySelector('.poll-pct-text');
                        const voteBtn = row.querySelector('.poll-vote-btn');

                        if (bar) bar.style.width = `${opt.percentage}%`;
                        if (pctText) pctText.textContent = `${opt.percentage}% (${opt.votes})`;
                        if (voteBtn) {
                            if (opt.index === data.user_voted_idx) {
                                voteBtn.classList.add('bg-purple-600', 'text-white', 'border-purple-700');
                                voteBtn.classList.remove('bg-white', 'text-gray-700');
                                voteBtn.innerHTML = '<i class="fas fa-check-circle mr-1"></i> Voted';
                            } else {
                                voteBtn.classList.remove('bg-purple-600', 'text-white', 'border-purple-700');
                                voteBtn.classList.add('bg-white', 'text-gray-700');
                                voteBtn.innerHTML = 'Vote';
                            }
                        }
                    }
                });
            }
        }
    } catch (e) {
        showToast('Error casting vote', 'error');
    }
}

async function handleEventRsvp(eventId, status, btnElement) {
    sfx.playClickSound();
    try {
        const res = await fetch('/api/rsvp-event', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event_id: eventId, status: status })
        });
        const data = await res.json();
        if (data.success) {
            showToast(`RSVP updated: ${status.toUpperCase()}!`, 'event');
            const card = document.getElementById(`event-card-${eventId}`);
            if (card) {
                const goingCountElem = card.querySelector('.event-going-count');
                if (goingCountElem) goingCountElem.textContent = `${data.going_count} Going`;
                
                card.querySelectorAll('.rsvp-btn').forEach(btn => {
                    btn.classList.remove('bg-emerald-600', 'bg-amber-600', 'text-white');
                    btn.classList.add('bg-gray-100', 'text-gray-700');
                });

                if (status === 'going') {
                    btnElement.classList.add('bg-emerald-600', 'text-white');
                    btnElement.classList.remove('bg-gray-100', 'text-gray-700');
                } else if (status === 'interested') {
                    btnElement.classList.add('bg-amber-600', 'text-white');
                    btnElement.classList.remove('bg-gray-100', 'text-gray-700');
                }
            }
        }
    } catch (e) {
        showToast('Error updating RSVP', 'error');
    }
}

async function togglePostLike(postId, btnElement) {
    sfx.playPokeSound();
    try {
        const res = await fetch('/api/like-post', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ post_id: postId })
        });
        const data = await res.json();
        if (data.success) {
            const countElem = document.getElementById(`post-likes-count-${postId}`);
            if (countElem) countElem.textContent = data.likes_count;

            const icon = btnElement.querySelector('i');
            if (data.is_liked) {
                icon.className = 'fas fa-heart text-red-500 mr-1.5 transition-transform scale-125';
                setTimeout(() => icon.classList.remove('scale-125'), 200);
            } else {
                icon.className = 'far fa-heart text-gray-500 mr-1.5';
            }
        }
    } catch (e) {
        showToast('Error liking post', 'error');
    }
}

async function addComment(postId, formElement) {
    sfx.playClickSound();
    const input = formElement.querySelector('input[name="content"]');
    const content = input.value.trim();
    if (!content) return;

    try {
        const res = await fetch('/api/comment-post', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ post_id: postId, content: content })
        });
        const data = await res.json();
        if (data.success) {
            input.value = '';
            showToast('Comment posted! (+2 Karma)', 'success');
            const commentsContainer = document.getElementById(`post-comments-list-${postId}`);
            if (commentsContainer) {
                const commentEl = document.createElement('div');
                commentEl.id = `comment-item-${data.comment.id}`;
                commentEl.className = 'flex items-start justify-between gap-2 text-xs group py-1';
                commentEl.innerHTML = `
                    <div class="flex items-start gap-2">
                        <img src="${data.comment.author_avatar}" class="w-6 h-6 rounded-full object-cover mt-0.5 border border-gray-200">
                        <div class="bg-gray-100 rounded-lg px-3 py-1.5 flex-1">
                            <span class="font-bold text-gray-900">${data.comment.author_name}</span>
                            <p class="text-gray-700 mt-0.5">${data.comment.content}</p>
                        </div>
                    </div>
                    <button onclick="handleDeleteComment('${data.comment.id}')" class="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 text-[10px] p-1" title="Delete comment">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                commentsContainer.appendChild(commentEl);
            }
        }
    } catch (e) {
        showToast('Error submitting comment', 'error');
    }
}

async function switchUserPersona(studentId) {
    try {
        const res = await fetch('/api/switch-user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: parseInt(studentId) })
        });
        const data = await res.json();
        if (data.success) {
            window.location.reload();
        }
    } catch (e) {
        showToast('Failed to switch persona', 'error');
    }
}

// Modal Helpers
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('flex');
        modal.classList.add('hidden');
    }
}

// Live Search & Document Ready
document.addEventListener('DOMContentLoaded', () => {
    initTheme();

    const searchInput = document.getElementById('global-search-input');
    const searchResults = document.getElementById('search-dropdown-results');

    if (searchInput && searchResults) {
        let debounceTimer;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            const query = e.target.value.trim();
            if (query.length < 2) {
                searchResults.classList.add('hidden');
                searchResults.innerHTML = '';
                return;
            }

            debounceTimer = setTimeout(async () => {
                try {
                    const res = await fetch(`/api/search-students?q=${encodeURIComponent(query)}`);
                    const students = await res.json();

                    if (students.length === 0) {
                        searchResults.innerHTML = `<div class="p-3 text-xs text-gray-500 text-center">No matching students found</div>`;
                        searchResults.classList.remove('hidden');
                        return;
                    }

                    searchResults.innerHTML = students.map(s => `
                        <a href="/profile/${s.id}" class="flex items-center gap-3 p-2.5 hover:bg-gray-100 transition border-b border-gray-100 last:border-b-0">
                            <img src="${s.avatar}" class="w-8 h-8 rounded-full object-cover border border-gray-300">
                            <div>
                                <div class="font-bold text-xs text-gray-900">${s.name} <span class="text-gray-400 font-normal">@${s.handle}</span></div>
                                <div class="text-[11px] text-gray-500">${s.department} • ${s.batch_title}</div>
                            </div>
                        </a>
                    `).join('');
                    searchResults.classList.remove('hidden');
                } catch (e) {
                    console.error('Search error', e);
                }
            }, 250);
        });

        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.classList.add('hidden');
            }
        });
    }

    // Scroll chat to bottom if on messages page
    const msgContainer = document.getElementById('messages-container');
    if (msgContainer) {
        msgContainer.scrollTop = msgContainer.scrollHeight;
    }
});
