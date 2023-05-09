const clientId = "1105638835855032380";
const DiscordRPC = require('discord-rpc');
const RPC = new DiscordRPC.Client({ transport: 'ipc' });

DiscordRPC.register(clientId);

async function setActivity() {
    if (!RPC) return;
    RPC.setActivity({
        details: 'Testing RPC',
        state: 'Messing Around',
        startTimestamp: Date.now(),
        largeImageKey: 'jellyfin-icon',
        largeImageText: 'placeholder',
        smallImageKey: 'jellyfin-icon',
        smallImageText: 'placeholder',
        instance: false,
        buttons: [
            {
                label: 'Test Button 1',
                url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                label: 'Test Button 2',
                url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            }
        ]
    });
}

RPC.on('ready', async () => {
    setActivity();

    setInterval(() => {
        setActivity();
    }, 15 * 1000);
});

RPC.login({ clientId: clientId }).catch(err => console.error(err));