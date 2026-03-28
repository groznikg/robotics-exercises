using System.Runtime.InteropServices;

namespace TurtleTeleop;

internal static class Terminal {
    const uint ICANON  = 0x00000002;
    const uint ECHO    = 0x00000008;
    const int  STDIN   = 0;
    const int  TCSANOW = 0;
    const int  VTIME   = 5;
    const int  VMIN    = 6;

    [StructLayout(LayoutKind.Sequential)]
    private struct Termios {
        public uint c_iflag;
        public uint c_oflag;
        public uint c_cflag;
        public uint c_lflag;
        public byte c_line;
        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 32)]
        public byte[] c_cc;
        public uint c_ispeed;
        public uint c_ospeed;
    }

    [DllImport("libc", EntryPoint = "tcgetattr")]
    private static extern int TcGetAttr(int fd, ref Termios t);

    [DllImport("libc", EntryPoint = "tcsetattr")]
    private static extern int TcSetAttr(int fd, int action, ref Termios t);

    [DllImport("libc", EntryPoint = "read")]
    private static extern int Read(int fd, byte[] buf, int count);

    private static Termios _saved;
    private static bool    _savedOk;

    public static void SetRawMode() {
        var t = new Termios { c_cc = new byte[32] };
        TcGetAttr(STDIN, ref t);
        _saved   = t;
        _savedOk = true;

        t.c_lflag    &= ~(ICANON | ECHO);
        t.c_cc[VMIN]  = 0; // don't wait for minimum number of bytes
        t.c_cc[VTIME] = 2; // return after 200ms if no key pressed
        TcSetAttr(STDIN, TCSANOW, ref t);
    }

    public static void Restore() {
        if (_savedOk)
            TcSetAttr(STDIN, TCSANOW, ref _saved);
    }

    public static char ReadKey() {
        var buf = new byte[1];
        return Read(STDIN, buf, 1) == 1 ? (char)buf[0] : '\0';
    }
}
