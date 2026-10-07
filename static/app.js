document.addEventListener('DOMContentLoaded', () => {
  const messagesContainer = document.getElementById('messagesContainer');
  const chatForm = document.getElementById('chatForm');
  const queryInput = document.getElementById('queryInput');
  const sendBtn = document.getElementById('sendBtn');
  const clearChatBtn = document.getElementById('clearChatBtn');
  const docsBadge = document.getElementById('docsBadge');
  const quickBtns = document.querySelectorAll('.quick-btn');

  // 1. Fetch Health and Knowledge Base Stats
  async function loadHealth() {
    try {
      const res = await fetch('/health');
      if (res.ok) {
        const data = await res.json();
        docsBadge.textContent = `${data.retriever_docs} Runbooks`;
      }
    } catch (e) {
      docsBadge.textContent = 'Offline';
    }
  }
  loadHealth();

  // 2. Auto-expand textarea
  queryInput.addEventListener('input', () => {
    queryInput.style.height = 'auto';
    queryInput.style.height = `${Math.min(queryInput.scrollHeight, 120)}px`;
  });

  // Enter to send (Shift+Enter for newline)
  queryInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event('submit'));
    }
  });

  // 3. Quick Action Buttons
  quickBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      const query = btn.getAttribute('data-query');
      if (query) {
        queryInput.value = query;
        chatForm.dispatchEvent(new Event('submit'));
      }
    });
  });

  // 4. Clear Chat
  clearChatBtn.addEventListener('click', () => {
    messagesContainer.innerHTML = '';
  });

  // 5. Append User Message
  function appendUserMessage(text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message user';
    msgDiv.innerHTML = `
      <div class="message-avatar">👤</div>
      <div class="message-content">
        <p>${escapeHtml(text)}</p>
      </div>
    `;
    messagesContainer.appendChild(msgDiv);
    scrollToBottom();
  }

  // 6. Append Assistant Message Container
  function createAssistantMessage() {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message assistant';
    msgDiv.innerHTML = `
      <div class="message-avatar">🐧</div>
      <div class="message-content">
        <div class="thoughts-box" style="display: none;">
          <div class="thought-header">
            <span class="thought-pulse"></span>
            <span>Agent Reasoning & Telemetry</span>
          </div>
          <ul class="thought-list"></ul>
        </div>
        <div class="tools-container"></div>
        <div class="markdown-body"></div>
      </div>
    `;
    messagesContainer.appendChild(msgDiv);
    scrollToBottom();

    return {
      element: msgDiv,
      thoughtsBox: msgDiv.querySelector('.thoughts-box'),
      thoughtList: msgDiv.querySelector('.thought-list'),
      toolsContainer: msgDiv.querySelector('.tools-container'),
      body: msgDiv.querySelector('.markdown-body')
    };
  }

  // 7. Chat Form Submit (SSE Streaming)
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = queryInput.value.trim();
    if (!query) return;

    queryInput.value = '';
    queryInput.style.height = 'auto';
    sendBtn.disabled = true;

    appendUserMessage(query);
    const assistantUi = createAssistantMessage();

    let fullMarkdown = '';

    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query })
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop(); // Keep partial chunk

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const jsonStr = line.replace('data: ', '').trim();
          if (!jsonStr) continue;

          try {
            const event = JSON.parse(jsonStr);

            if (event.type === 'thought') {
              assistantUi.thoughtsBox.style.display = 'block';
              const li = document.createElement('li');
              li.textContent = event.content;
              assistantUi.thoughtList.appendChild(li);
              scrollToBottom();

            } else if (event.type === 'tool_call') {
              const card = document.createElement('div');
              card.className = 'tool-card';
              card.id = `tool-${event.tool}`;
              card.innerHTML = `
                <div class="tool-card-header">
                  <span>⚙️ Executing Safe Tool: <strong>${escapeHtml(event.tool)}</strong></span>
                  <span>Running...</span>
                </div>
              `;
              assistantUi.toolsContainer.appendChild(card);
              scrollToBottom();

            } else if (event.type === 'tool_result') {
              const card = document.getElementById(`tool-${event.tool}`);
              if (card) {
                card.querySelector('.tool-card-header').innerHTML = `
                  <span>⚙️ Tool Result: <strong>${escapeHtml(event.tool)}</strong></span>
                  <span style="color: ${event.success ? '#10b981' : '#f43f5e'}">${event.success ? 'Success (Exit ' + event.exit_code + ')' : 'Failed'}</span>
                `;
                const outDiv = document.createElement('div');
                outDiv.className = 'tool-output';
                outDiv.textContent = event.output || '(No output)';
                card.appendChild(outDiv);
              }
              scrollToBottom();

            } else if (event.type === 'token') {
              fullMarkdown += event.content;
              assistantUi.body.innerHTML = renderMarkdown(fullMarkdown);
              attachCopyButtons(assistantUi.body);
              scrollToBottom();

            } else if (event.type === 'done') {
              // Agent finished
              const pulse = assistantUi.thoughtsBox.querySelector('.thought-pulse');
              if (pulse) pulse.style.display = 'none';
            }
          } catch (err) {
            console.error('Error parsing SSE event:', err);
          }
        }
      }
    } catch (err) {
      assistantUi.body.innerHTML = `<p style="color: #f43f5e;">Error: ${escapeHtml(err.message)}</p>`;
    } finally {
      sendBtn.disabled = false;
      queryInput.focus();
    }
  });

  // Utilities
  function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Lightweight Markdown Renderer (Headers, bold, codeblocks, lists)
  function renderMarkdown(md) {
    if (!md) return '';

    // Code blocks with language
    let html = md.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (match, lang, code) => {
      return `
        <pre><button class="copy-code-btn" onclick="copyCode(this)">Copy</button><code class="language-${lang}">${escapeHtml(code.trim())}</code></pre>
      `;
    });

    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

    // Bold
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Bullet lists
    html = html.replace(/^\- (.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

    // Paragraphs
    html = html.split('\n\n').map(p => {
      if (p.startsWith('<h') || p.startsWith('<pre') || p.startsWith('<ul')) return p;
      return `<p>${p.replace(/\n/g, '<br>')}</p>`;
    }).join('');

    return html;
  }

  window.copyCode = function(button) {
    const code = button.nextElementSibling.textContent;
    navigator.clipboard.writeText(code).then(() => {
      const originalText = button.textContent;
      button.textContent = 'Copied!';
      setTimeout(() => {
        button.textContent = originalText;
      }, 2000);
    });
  };

  function attachCopyButtons(container) {
    // Buttons are already inline with onclick="copyCode(this)"
  }
});
