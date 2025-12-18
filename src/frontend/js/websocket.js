/**
 * WebSocket client for MuLyCue
 * Handles real-time communication with backend
 */

class MuLyCueWebSocket {
    constructor(url = null) {
        this.url = url || `ws://${window.location.host}/ws`;
        this.ws = null;
        this.callbacks = {
            position_update: [],
            entry_change: [],
            section_change: [],
            beat_tick: [],
            playback_state: [],
            song_loaded: [],
            error: []
        };
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.isConnected = false;
    }

    connect() {
        console.log('Connecting to WebSocket:', this.url);
        
        try {
            this.ws = new WebSocket(this.url);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
                
                // Send ping to keep connection alive
                this.startPingInterval();
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (e) {
                    console.error('Error parsing WebSocket message:', e);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.triggerCallbacks('error', { error: 'Connection error' });
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.stopPingInterval();
                
                // Attempt reconnection
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);
                    setTimeout(() => this.connect(), this.reconnectDelay * this.reconnectAttempts);
                }
            };
        } catch (e) {
            console.error('Error creating WebSocket:', e);
            this.isConnected = false;
            this.updateConnectionStatus(false);
        }
    }

    disconnect() {
        if (this.ws) {
            this.stopPingInterval();
            this.ws.close();
            this.ws = null;
            this.isConnected = false;
            this.updateConnectionStatus(false);
        }
    }

    send(type, payload = {}) {
        if (!this.isConnected || !this.ws) {
            console.warn('WebSocket not connected, cannot send message');
            return false;
        }

        try {
            this.ws.send(JSON.stringify({ type, ...payload }));
            return true;
        } catch (e) {
            console.error('Error sending WebSocket message:', e);
            return false;
        }
    }

    handleMessage(data) {
        const type = data.type;
        
        if (!type) {
            console.warn('Received message without type:', data);
            return;
        }

        console.log('WebSocket message:', type, data);
        this.triggerCallbacks(type, data);
    }

    on(event, callback) {
        if (this.callbacks[event]) {
            this.callbacks[event].push(callback);
        } else {
            console.warn(`Unknown event type: ${event}`);
        }
    }

    off(event, callback) {
        if (this.callbacks[event]) {
            const index = this.callbacks[event].indexOf(callback);
            if (index > -1) {
                this.callbacks[event].splice(index, 1);
            }
        }
    }

    triggerCallbacks(event, data) {
        if (this.callbacks[event]) {
            this.callbacks[event].forEach(callback => {
                try {
                    callback(data);
                } catch (e) {
                    console.error(`Error in ${event} callback:`, e);
                }
            });
        }
    }

    startPingInterval() {
        this.pingInterval = setInterval(() => {
            if (this.isConnected) {
                this.send('ping');
            }
        }, 30000); // Ping every 30 seconds
    }

    stopPingInterval() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
    }

    updateConnectionStatus(connected) {
        // Update UI elements if they exist
        const statusIndicator = document.getElementById('wsStatus');
        const statusText = document.getElementById('wsText');
        
        if (statusIndicator) {
            statusIndicator.textContent = connected ? '🟢' : '⚫';
            statusIndicator.className = `status-indicator ${connected ? 'connected' : 'disconnected'}`;
        }
        
        if (statusText) {
            statusText.textContent = connected ? 'Connected' : 'Disconnected';
        }
    }

    // Convenience methods for common actions
    play() {
        return this.send('play');
    }

    pause() {
        return this.send('pause');
    }

    stop() {
        return this.send('stop');
    }

    seek(position) {
        return this.send('seek', { position });
    }

    transpose(semitones) {
        return this.send('transpose', { semitones });
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MuLyCueWebSocket;
}

