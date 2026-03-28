using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using TurtleTeleop;

const string ConfigPath   = "/ros2_ws/src/turtle_teleop_wasd/config/keybindings.json";
const string RosbridgeUri = "ws://localhost:9090";

var cfg = KeyBindings.Load(ConfigPath);

Console.WriteLine("[INFO] Connecting to rosbridge...");
using var ws = new ClientWebSocket();

for (int retries = 10; retries > 0; retries--) {
    try {
        await ws.ConnectAsync(new Uri(RosbridgeUri), CancellationToken.None);
        break;
    } catch {
        if (retries == 1) {
            Console.WriteLine("[ERROR] Could not connect to rosbridge.");
            return;
        }
        Console.WriteLine($"[INFO] Waiting for rosbridge... ({retries - 1} retries left)");
        await Task.Delay(500);
    }
}

Console.WriteLine("[INFO] Connected.");

await Publish(ws, new {
    op    = "advertise",
    topic = "/turtle1/cmd_vel",
    type  = "geometry_msgs/Twist"
});

Terminal.SetRawMode();

Console.CancelKeyPress += async (_, e) => {
    e.Cancel = true;
    Terminal.Restore();
    await Stop(ws);
    Environment.Exit(0);
};

Console.WriteLine("=== TurtleBot WASD Teleop (C#) ===");
Console.WriteLine($"  {cfg.Forward}=forward   {cfg.Backward}=backward");
Console.WriteLine($"  {cfg.Left}=rotate L  {cfg.Right}=rotate R  {cfg.Quit}=quit");

while (true) {
    char key = char.ToLower(Terminal.ReadKey());

    double linear = 0.0, angular = 0.0;

    if      (key == cfg.Quit)     break;
    else if (key == cfg.Forward)  linear  =  cfg.LinearSpeed;
    else if (key == cfg.Backward) linear  = -cfg.LinearSpeed;
    else if (key == cfg.Left)     angular =  cfg.AngularSpeed;
    else if (key == cfg.Right)    angular = -cfg.AngularSpeed;

    await Publish(ws, new {
        op    = "publish",
        topic = "/turtle1/cmd_vel",
        msg   = new {
            linear  = new { x = linear,  y = 0.0, z = 0.0 },
            angular = new { x = 0.0, y = 0.0, z = angular }
        }
    });
}

Terminal.Restore();
await Stop(ws);
Console.WriteLine("Stopped.");

static async Task Publish(ClientWebSocket socket, object data) {
    var bytes = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(data));
    await socket.SendAsync(bytes, WebSocketMessageType.Text, true, CancellationToken.None);
}

static async Task Stop(ClientWebSocket socket) {
    try {
        await Publish(socket, new {
            op    = "publish",
            topic = "/turtle1/cmd_vel",
            msg   = new {
                linear  = new { x = 0.0, y = 0.0, z = 0.0 },
                angular = new { x = 0.0, y = 0.0, z = 0.0 }
            }
        });
    } catch { }
}
