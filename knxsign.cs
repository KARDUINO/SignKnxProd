using System;
using System.Reflection;

class Program
{
    static void Main(string[] args)
    {
        if (args.Length != 2)
        {
            Console.WriteLine("Syntax: <path to ETS installation> <path to files to be signed>");
            return;
        }

        string dllLocation = System.IO.Path.Combine(args[0], "Knx.Ets.Converter.ConverterEngine.dll");

        if (!System.IO.File.Exists(dllLocation))
        {
            Console.WriteLine("Can't load Knx.Ets.Converter.ConverterEngine.dll at location: " + dllLocation);
            return;
        }

        string signDir = args[1];

        if (!System.IO.Directory.Exists(signDir))
        {
            Console.WriteLine("Directory to be signed doesn't exist! Location: " + signDir);
            return;
        }

        var asm = Assembly.LoadFrom(dllLocation);
        var type = asm.GetType("Knx.Ets.Converter.ConverterEngine.ConverterEngine");
        var mi = type.GetMethod("SignOutputFiles", BindingFlags.Static | BindingFlags.NonPublic);
        mi.Invoke(null, new object[] { signDir });
    }
}
