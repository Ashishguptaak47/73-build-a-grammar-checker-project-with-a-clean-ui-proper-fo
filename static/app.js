document.addEventListener('DOMContentLoaded', () => {
    const editor = document.getElementById('editor');
    const backdrop = document.getElementById('backdrop');
    const statWords = document.getElementById('stat-words');
    const statChars = document.getElementById('stat-chars');
    const metricEase = document.getElementById('metric-ease');
    const metricGrade = document.getElementById('metric-grade');
    const metricLevel = document.getElementById('metric-level');
    const issuesList = document.getElementById('issues-list');
    const issuesCount = document.getElementById('issues-count');
    const filterSelect = document.getElementById('filter-category');
    const btnFixAll = document.getElementById('btn-fix-all');
    const btnSample = document.getElementById('btn-sample');

    let debounceTimer = null;
    let currentIssues = [];

    const sampleText = `he don't understand the the problem. in order to solve this issue, i think your welcome to review it. The system will loose performance due to the fact that their going too fast ,right?`;

    btnSample.addEventListener('click', () => {
        editor.value = sampleText;
        triggerCheck();
    });

    editor.addEventListener('input', () => {
        updateBackdropScroll();
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(triggerCheck, 250);
    });

    editor.addEventListener('scroll', updateBackdropScroll);
    filterSelect.addEventListener('change', renderIssues);

    btnFixAll.addEventListener('click', async () => {
        const text = editor.value;
        if (!text.trim()) return;

        try {
            const res = await fetch('/api/fix-all', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            const data = await res.json();
            editor.value = data.fixed_text;
            triggerCheck();
        } catch (err) {
            console.error('Failed to auto fix:', err);
        }
    });

    function updateBackdropScroll() {
        backdrop.scrollTop = editor.scrollTop;
        backdrop.scrollLeft = editor.scrollLeft;
    }

    async function triggerCheck() {
        const text = editor.value;
        statChars.textContent = `${text.length} characters`;
        
        try {
            const res = await fetch('/api/check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            const data = await res.json();
            
            statWords.textContent = `${data.metrics.word_count} words`;
            metricEase.textContent = data.metrics.flesch_reading_ease;
            metricGrade.textContent = data.metrics.flesch_kincaid_grade;
            metricLevel.textContent = data.metrics.reading_level;
            
            currentIssues = data.issues;
            issuesCount.textContent = currentIssues.length;
            btnFixAll.disabled = currentIssues.length === 0;

            renderHighlights(text, currentIssues);
            renderIssues();
        } catch (err) {
            console.error('Check error:', err);
        }
    }

    function renderHighlights(text, issues) {
        if (!issues || issues.length === 0) {
            backdrop.innerHTML = escapeHtml(text);
            return;
        }

        let result = '';
        let lastIndex = 0;

        issues.forEach(issue => {
            if (issue.start >= lastIndex && issue.end <= text.length) {
                result += escapeHtml(text.slice(lastIndex, issue.start));
                const snippet = escapeHtml(text.slice(issue.start, issue.end));
                result += `<mark class="hl-${issue.category}">${snippet}</mark>`;
                lastIndex = issue.end;
            }
        });

        result += escapeHtml(text.slice(lastIndex));
        backdrop.innerHTML = result;
    }

    function renderIssues() {
        const filter = filterSelect.value;
        const filtered = filter === 'all' 
            ? currentIssues 
            : currentIssues.filter(i => i.category === filter);

        if (filtered.length === 0) {
            issuesList.innerHTML = `<div class="empty-state"><p>No issues found ${filter !== 'all' ? 'for this category' : ''}.</p></div>`;
            return;
        }

        issuesList.innerHTML = '';
        filtered.forEach(issue => {
            const div = document.createElement('div');
            div.className = 'issue-item';
            div.innerHTML = `
                <div class="issue-header">
                    <span class="issue-tag tag-${issue.category}">${issue.category}</span>
                    <span class="issue-matched">"${escapeHtml(issue.matched_text)}"</span>
                </div>
                <p class="issue-msg">${escapeHtml(issue.message)}</p>
                <div class="issue-actions"></div>
            `;

            const actions = div.querySelector('.issue-actions');
            issue.replacements.forEach(rep => {
                const btn = document.createElement('button');
                btn.className = 'btn-fix';
                btn.textContent = `Replace with "${rep}"`;
                btn.addEventListener('click', () => applySingleFix(issue.id, rep));
                actions.appendChild(btn);
            });

            issuesList.appendChild(div);
        });
    }

    async function applySingleFix(issueId, replacement) {
        try {
            const res = await fetch('/api/fix', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: editor.value,
                    issue_id: issueId,
                    replacement: replacement
                })
            });
            const data = await res.json();
            editor.value = data.fixed_text;
            triggerCheck();
        } catch (err) {
            console.error('Failed to apply fix:', err);
        }
    }

    function escapeHtml(str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // Initial kick-off with sample
    editor.value = sampleText;
    triggerCheck();
});
