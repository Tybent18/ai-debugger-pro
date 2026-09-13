const vscode = require("vscode");
const { spawn } = require("child_process");

function execute(command, output) {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showWarningMessage("Open a source file first.");
    return;
  }
  editor.document.save().then(() => {
    output.show(true);
    output.appendLine(`\n$ ai-debugger-pro ${command} ${editor.document.fileName}`);
    const process = spawn("ai-debugger-pro", [command, editor.document.fileName], { shell: false });
    process.stdout.on("data", data => output.append(data.toString()));
    process.stderr.on("data", data => output.append(data.toString()));
    process.on("error", error => output.appendLine(`Unable to launch CLI: ${error.message}`));
    process.on("close", code => output.appendLine(`\nExited with code ${code}`));
  });
}

function activate(context) {
  const output = vscode.window.createOutputChannel("AI Debugger Pro");
  context.subscriptions.push(output);
  context.subscriptions.push(
    vscode.commands.registerCommand("aiDebuggerPro.run", () => execute("run", output)),
    vscode.commands.registerCommand("aiDebuggerPro.diagnose", () => execute("diagnose", output))
  );
}

function deactivate() {}

module.exports = { activate, deactivate };

