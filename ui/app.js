function ccbApp() {
    return {
        projects: [],
        chats: [],
        currentChat: null,
        currentChatId: null,
        selectedProject: "",
        query: "",
        ready: false,
        debounceTimer: null,
        lastVersion: null,
        expandedProjects: {},
        transcriptSearch: "",
        matchCount: 0,
        currentMatch: 0,
        jumpToMatch: "",
        allMatches: [],
        searchBoxFocused: false,
        contextMenu: { visible: false, x: 0, y: 0, hasSelection: false },
        isDarkMode: true,

        async init() {
            console.log("init() called");
            this.initTheme();
            // Ctrl+R to refresh
            window.addEventListener("keydown", (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === "r") {
                    e.preventDefault();
                    location.reload();
                }
            });
            // Wait for pywebview to be ready before loading data
            window.addEventListener("pywebviewready", async () => {
                console.log("pywebviewready event fired");
                try {
                    console.log("Calling get_projects...");
                    this.projects = await window.pywebview.api.get_projects();
                    console.log("Got projects:", this.projects);
                    console.log("Calling get_chats...");
                    this.chats = await window.pywebview.api.get_chats();
                    console.log("Got chats:", this.chats);
                    this.ready = true;

                    // Restore previously open chat
                    try {
                        const lastChatId = await window.pywebview.api.get_last_chat();
                        if (lastChatId && this.chats.find(c => c.id === lastChatId)) {
                            this.selectChat(lastChatId);
                        }
                    } catch (e) {
                        console.log("Could not restore last chat");
                    }

                    // Poll for backend restarts (dev mode auto-reload)
                    this.startVersionPoll();
                } catch (e) {
                    console.error("Failed to load initial data:", e);
                }
            });
        },

        async startVersionPoll() {
            setInterval(async () => {
                try {
                    const version = await window.pywebview.api.get_version();
                    if (this.lastVersion === null) {
                        this.lastVersion = version;
                    } else if (version !== this.lastVersion) {
                        console.log("Backend restarted, reloading page...");
                        location.reload();
                    }
                } catch (e) {
                    // Silently fail on poll errors
                }
            }, 2000);
        },

        async onProjectChange() {
            await this.updateChats();
        },

        async onSearch() {
            console.log("Search triggered with query:", this.query);
            await this.updateChats();
        },

        async updateChats() {
            try {
                console.log("updateChats called with project:", this.selectedProject, "query:", this.query);
                this.chats = await window.pywebview.api.get_chats(
                    this.selectedProject || null,
                    this.query || null
                );
                console.log("API returned", this.chats.length, "chats");
                if (this.currentChatId && !this.chats.find(c => c.id === this.currentChatId)) {
                    this.currentChat = null;
                    this.currentChatId = null;
                }
            } catch (e) {
                console.error("Failed to update chats:", e);
            }
        },

        async selectChat(chatId) {
            try {
                this.currentChatId = chatId;
                await window.pywebview.api.save_last_chat(chatId);
                this.currentChat = await window.pywebview.api.get_chat(chatId);
                if (this.currentChat) {
                    // Pass sidebar search to transcript search
                    this.transcriptSearch = this.query;

                    this.$nextTick(() => {
                        Prism.highlightAll();
                        this.updateSearchMatches();
                    });
                }
            } catch (e) {
                console.error("Failed to load chat:", e);
                this.currentChat = null;
                this.currentChatId = null;
            }
        },

        async copyCurrentChat() {
            if (!this.currentChat) return;
            try {
                let text = `Chat: ${this.currentChat.name}\nProject: ${this.currentChat.project_path}\n\n`;
                for (const turn of this.currentChat.turns) {
                    text += `\n${turn.role.toUpperCase()}:\n`;
                    for (const block of turn.content) {
                        if (block.type === "text") {
                            text += block.text + "\n";
                        } else if (block.type === "tool_use") {
                            text += `Tool: ${block.name}\n${JSON.stringify(block.input, null, 2)}\n`;
                        } else if (block.type === "tool_result") {
                            text += `Result:\n${block.content}\n`;
                        }
                    }
                }
                await window.pywebview.api.copy_to_clipboard(text);
                alert("Chat copied to clipboard");
            } catch (e) {
                console.error("Failed to copy:", e);
            }
        },

        formatDate(dateStr) {
            if (!dateStr) return "";
            const date = new Date(dateStr);
            return date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        },

        renderMarkdown(text) {
            if (!window.marked) return text;
            return window.marked.parse ? window.marked.parse(text) : window.marked(text);
        },

        debounce(fn, delay) {
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(fn, delay);
        },

        getGroupedChats() {
            const groups = {};
            for (const chat of this.chats) {
                const path = chat.project_path;
                if (!groups[path]) {
                    groups[path] = { path, name: path.split("/").pop(), chats: [] };
                }
                groups[path].chats.push(chat);
            }
            return Object.values(groups).sort((a, b) => a.name.localeCompare(b.name));
        },

        toggleProject(path) {
            this.$nextTick(() => {
                this.expandedProjects[path] = !this.expandedProjects[path];
            });
        },

        isProjectExpanded(path) {
            return this.expandedProjects[path] || false;
        },

        highlightText(text) {
            if (!this.transcriptSearch || !text) return text;
            const query = this.transcriptSearch.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
            const regex = new RegExp(`(${query})`, "gi");
            return text.replace(regex, '<mark style="background-color: transparent; color: #fbbf24; text-decoration: underline; text-decoration-color: #fbbf24; text-decoration-thickness: 2px;">$1</mark>');
        },

        updateSearchMatches() {
            this.$nextTick(() => {
                const marks = document.querySelectorAll('mark');
                this.allMatches = Array.from(marks);
                this.matchCount = marks.length;
                this.currentMatch = this.matchCount > 0 ? 1 : 0;
                this.jumpToMatch = "";
                if (this.matchCount > 0) {
                    this.scrollToMatch(0);
                }
            });
        },

        scrollToMatch(index) {
            // Re-query marks in case DOM was updated
            const marks = document.querySelectorAll('mark');
            if (index < 0 || index >= marks.length) return;
            // Remove current-match class from all marks
            marks.forEach(m => m.classList.remove('current-match'));
            // Add it to the target match
            marks[index].classList.add('current-match');
            this.currentMatch = index + 1;
            marks[index].scrollIntoView({ behavior: "smooth", block: "center" });
        },

        previousMatch() {
            if (this.matchCount === 0) return;
            if (this.currentMatch <= 1) {
                this.scrollToMatch(this.matchCount - 1);
            } else {
                this.scrollToMatch(this.currentMatch - 2);
            }
        },

        nextMatch() {
            if (this.matchCount === 0) return;
            if (this.currentMatch >= this.matchCount) {
                this.scrollToMatch(0);
            } else {
                this.scrollToMatch(this.currentMatch);
            }
        },

        goToMatch() {
            const num = parseInt(this.jumpToMatch);
            if (num >= 1 && num <= this.matchCount) {
                this.scrollToMatch(num - 1);
                this.jumpToMatch = "";
            }
        },

        showContextMenu(event) {
            event.preventDefault();
            this.contextMenu.x = event.clientX;
            this.contextMenu.y = event.clientY;
            this.contextMenu.hasSelection = window.getSelection().toString().length > 0;
            this.contextMenu.visible = true;
        },

        copySelected() {
            const selected = window.getSelection().toString();
            if (selected) {
                navigator.clipboard.writeText(selected);
            }
            this.contextMenu.visible = false;
        },

        selectAll() {
            const selection = window.getSelection();
            const range = document.createRange();
            const transcriptDiv = document.getElementById('transcript');
            if (transcriptDiv) {
                range.selectNodeContents(transcriptDiv);
                selection.removeAllRanges();
                selection.addRange(range);
            }
            this.contextMenu.visible = false;
        },

        initTheme() {
            const saved = localStorage.getItem('theme');
            this.isDarkMode = saved ? saved === 'dark' : true;
            this.applyTheme();
        },

        toggleTheme() {
            this.isDarkMode = !this.isDarkMode;
            localStorage.setItem('theme', this.isDarkMode ? 'dark' : 'light');
            this.applyTheme();
        },

        applyTheme() {
            if (this.isDarkMode) {
                document.body.classList.remove('light-mode');
            } else {
                document.body.classList.add('light-mode');
            }
        },
    };
}

