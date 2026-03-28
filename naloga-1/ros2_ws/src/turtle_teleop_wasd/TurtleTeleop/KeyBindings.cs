using System.Text.Json;
using System.Text.Json.Serialization;

namespace TurtleTeleop;

public class KeyBindings {
    [JsonPropertyName("key_forward")]  public string KeyForward  { get; set; } = "w";
    [JsonPropertyName("key_backward")] public string KeyBackward { get; set; } = "s";
    [JsonPropertyName("key_left")]     public string KeyLeft     { get; set; } = "a";
    [JsonPropertyName("key_right")]    public string KeyRight    { get; set; } = "d";
    [JsonPropertyName("key_quit")]     public string KeyQuit     { get; set; } = "q";
    [JsonPropertyName("linear_speed")] public double LinearSpeed  { get; set; } = 2.0;
    [JsonPropertyName("angular_speed")]public double AngularSpeed { get; set; } = 2.0;

    public char Forward  => KeyForward.FirstOrDefault('w');
    public char Backward => KeyBackward.FirstOrDefault('s');
    public char Left     => KeyLeft.FirstOrDefault('a');
    public char Right    => KeyRight.FirstOrDefault('d');
    public char Quit     => KeyQuit.FirstOrDefault('q');

    public static KeyBindings Load(string path) {
        try {
            if (File.Exists(path)) {
                var opts = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
                return JsonSerializer.Deserialize<KeyBindings>(File.ReadAllText(path), opts)
                       ?? new KeyBindings();
            }
        } catch (Exception ex) {
            Console.WriteLine($"[WARN] Could not load config: {ex.Message}. Using defaults.");
        }
        return new KeyBindings();
    }
}
