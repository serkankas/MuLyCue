/**
 * Panel Manager for MuLyCue
 * Manages panel lifecycle, layouts, and multi-window synchronization
 */

class PanelManager {
    constructor() {
        this.panels = new Map();
        this.snapToEdges = true;
        this.setupBroadcastChannel();
        this.loadLayout();
    }
    
    addPanel(type, config = {}) {
        const PanelClass = {
            'lyrics': LyricsPanel,
            'chords': ChordsPanel,
            'bpm': BPMPanel,
            'beat': BeatPanel,
            'section': SectionPanel,
            'timeline': TimelinePanel,
            'transpose': TransposePanel
        }[type];
        
        if (!PanelClass) {
            console.error(`Unknown panel type: ${type}`);
            return null;
        }
        
        const panel = new PanelClass(config);
        this.panels.set(panel.id, panel);
        
        const container = document.getElementById('panel-container');
        if (container) {
            container.appendChild(panel.element);
        }
        
        return panel;
    }
    
    removePanel(panelId) {
        const panel = this.panels.get(panelId);
        if (panel) {
            panel.element.remove();
            this.panels.delete(panelId);
            this.saveLayout();
        }
    }
    
    getPanel(panelId) {
        return this.panels.get(panelId);
    }
    
    getAllPanels() {
        return Array.from(this.panels.values());
    }
    
    getPanelsByType(type) {
        return this.getAllPanels().filter(p => p.type === type);
    }
    
    saveLayout() {
        const layout = this.getAllPanels().map(panel => ({
            type: panel.type,
            config: panel.config
        }));
        
        localStorage.setItem('mulycue-player-layout', JSON.stringify(layout));
        console.log('Layout saved:', layout.length, 'panels');
    }
    
    loadLayout(layoutName = null) {
        // Clear existing panels
        this.clearAllPanels();
        
        let layout;
        
        if (layoutName && LAYOUT_PRESETS[layoutName]) {
            // Load preset
            layout = LAYOUT_PRESETS[layoutName];
        } else {
            // Load saved layout
            const saved = localStorage.getItem('mulycue-player-layout');
            if (saved) {
                try {
                    layout = JSON.parse(saved);
                } catch (e) {
                    console.error('Error loading saved layout:', e);
                    layout = null;
                }
            }
        }
        
        if (layout && Array.isArray(layout)) {
            layout.forEach(({ type, config }) => this.addPanel(type, config));
        } else {
            // Load default layout
            this.loadDefaultLayout();
        }
    }
    
    loadDefaultLayout() {
        this.addPanel('lyrics', { x: 20, y: 20, width: 600, height: 400 });
        this.addPanel('chords', { x: 640, y: 20, width: 300, height: 200 });
        this.addPanel('bpm', { x: 640, y: 240, width: 300, height: 200 });
        this.addPanel('timeline', { x: 20, y: 440, width: 920, height: 120 });
    }
    
    clearAllPanels() {
        this.getAllPanels().forEach(panel => {
            panel.element.remove();
        });
        this.panels.clear();
    }
    
    resetLayout() {
        if (confirm('Reset to default layout? This will clear your custom layout.')) {
            localStorage.removeItem('mulycue-player-layout');
            this.loadDefaultLayout();
        }
    }
    
    exportLayout() {
        const layout = this.getAllPanels().map(panel => ({
            type: panel.type,
            config: panel.config
        }));
        
        const dataStr = JSON.stringify(layout, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = 'mulycue-layout.json';
        link.click();
        
        URL.revokeObjectURL(url);
    }
    
    importLayout(file) {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            try {
                const layout = JSON.parse(e.target.result);
                this.clearAllPanels();
                layout.forEach(({ type, config }) => this.addPanel(type, config));
                this.saveLayout();
                showToast('Layout imported successfully', 'success');
            } catch (error) {
                console.error('Error importing layout:', error);
                showToast('Error importing layout', 'error');
            }
        };
        
        reader.readAsText(file);
    }
    
    setupBroadcastChannel() {
        // For multi-window synchronization
        this.channel = new BroadcastChannel('mulycue-sync');
        
        this.channel.addEventListener('message', (event) => {
            this.updateAllPanels(event.data);
        });
    }
    
    broadcast(data) {
        // Broadcast to other windows
        this.channel.postMessage(data);
        
        // Update local panels
        this.updateAllPanels(data);
    }
    
    updateAllPanels(data) {
        this.getAllPanels().forEach(panel => {
            try {
                panel.updateContent(data);
            } catch (error) {
                console.error(`Error updating panel ${panel.id}:`, error);
            }
        });
    }
    
    openNewWindow() {
        const url = 'player-window.html';
        const features = 'width=1280,height=800,resizable=yes';
        const newWindow = window.open(url, `mulycue-window-${Date.now()}`, features);
        
        if (newWindow) {
            showToast('New window opened', 'success');
        } else {
            showToast('Failed to open new window. Check popup blocker.', 'error');
        }
    }
    
    toggleSnapToEdges() {
        this.snapToEdges = !this.snapToEdges;
        return this.snapToEdges;
    }
}

// Layout Presets
const LAYOUT_PRESETS = {
    default: [
        { type: 'lyrics', config: { x: 20, y: 20, width: 600, height: 400 } },
        { type: 'chords', config: { x: 640, y: 20, width: 300, height: 200 } },
        { type: 'bpm', config: { x: 640, y: 240, width: 300, height: 200 } },
        { type: 'timeline', config: { x: 20, y: 440, width: 920, height: 120 } }
    ],
    
    vocalist: [
        { type: 'lyrics', config: { x: 20, y: 20, width: window.innerWidth - 40, height: window.innerHeight - 160 } },
        { type: 'timeline', config: { x: 20, y: window.innerHeight - 120, width: window.innerWidth - 40, height: 100 } }
    ],
    
    guitarist: [
        { type: 'lyrics', config: { x: 20, y: 20, width: 400, height: 300 } },
        { type: 'chords', config: { x: 440, y: 20, width: 400, height: 400 } },
        { type: 'bpm', config: { x: 860, y: 20, width: 200, height: 200 } },
        { type: 'beat', config: { x: 860, y: 240, width: 200, height: 180 } },
        { type: 'transpose', config: { x: 440, y: 440, width: 200, height: 120 } }
    ],
    
    drummer: [
        { type: 'bpm', config: { x: 20, y: 20, width: 400, height: 400 } },
        { type: 'beat', config: { x: 440, y: 20, width: 400, height: 400 } },
        { type: 'section', config: { x: 20, y: 440, width: 820, height: 100 } },
        { type: 'timeline', config: { x: 20, y: 560, width: 820, height: 100 } }
    ],
    
    minimal: [
        { type: 'lyrics', config: { x: 20, y: 20, width: 800, height: 500 } },
        { type: 'chords', config: { x: 840, y: 20, width: 300, height: 250 } }
    ],
    
    fullscreen: [
        { type: 'lyrics', config: { x: 0, y: 0, width: window.innerWidth, height: window.innerHeight } }
    ]
};

// Initialize global panel manager
window.panelManager = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.panelManager = new PanelManager();
    console.log('Panel Manager initialized');
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PanelManager, LAYOUT_PRESETS };
}

