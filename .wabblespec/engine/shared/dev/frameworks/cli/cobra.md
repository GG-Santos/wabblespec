# Cobra (Go CLI)

Loaded by Apply when cobra import or go.mod with cobra is detected.

## Version baseline

cobra v1.8+. Uses `cobra.Command` with `RunE` (returns error) rather than `Run` (panics).

## Command structure

```go
package main

import (
    "os"
    "github.com/spf13/cobra"
    "github.com/spf13/viper"
)

var rootCmd = &cobra.Command{
    Use:   "tool",
    Short: "One-line description",
    Long:  `Multi-line description for --help.`,
}

var subCmd = &cobra.Command{
    Use:   "sub [flags] <arg>",
    Short: "Subcommand description",
    Args:  cobra.ExactArgs(1),
    RunE: func(cmd *cobra.Command, args []string) error {
        // return error to set exit code 1; cobra prints it
        return nil
    },
}

func init() {
    rootCmd.AddCommand(subCmd)
    subCmd.Flags().StringP("output", "o", "", "output file")
    subCmd.Flags().BoolP("verbose", "v", false, "verbose output")
}

func main() {
    if err := rootCmd.Execute(); err != nil {
        os.Exit(1)
    }
}
```

## Flags: Cobra + Viper pattern

Use Viper for configuration binding — it handles flag, env var, and config file hierarchy:

```go
func init() {
    cobra.OnInitialize(initConfig)
    rootCmd.PersistentFlags().String("config", "", "config file")
    viper.BindPFlag("config", rootCmd.PersistentFlags().Lookup("config"))
}

func initConfig() {
    viper.SetEnvPrefix("TOOL")
    viper.AutomaticEnv()
    // reads TOOL_OUTPUT, TOOL_VERBOSE, etc.
}
```

## Error handling

```go
RunE: func(cmd *cobra.Command, args []string) error {
    if err := doWork(); err != nil {
        // cobra prints "Error: {message}" and exits 1
        return fmt.Errorf("operation failed: %w", err)
    }
    return nil
},
```

For usage errors (bad args): `return cmd.Usage()` + print message to stderr.
For non-zero exit without error message: `os.Exit(code)` after printing to stderr.

## Stderr vs stdout

```go
cmd.Println("data output")      // stdout
cmd.PrintErr("error message")   // stderr
fmt.Fprintln(os.Stderr, "...")  // stderr (alternative)
```

## Distribution

- Cross-compile with `GOOS` / `GOARCH`
- Single binary — no runtime dependency
- `goreleaser` for multi-platform release automation (GitHub Actions + GoReleaser action)
- Homebrew formula for macOS distribution

## Shell completion

Cobra generates completion scripts automatically:
```go
rootCmd.AddCommand(completionCmd) // or cobra built-in completion command
```

Enable in spec if the tool is user-facing (not just called by scripts).

## Testing

```go
func TestSubCommand(t *testing.T) {
    cmd := rootCmd
    buf := new(bytes.Buffer)
    cmd.SetOut(buf)
    cmd.SetArgs([]string{"sub", "arg", "--output", "out.txt"})
    err := cmd.Execute()
    assert.NoError(t, err)
    assert.Contains(t, buf.String(), "expected")
}
```

Set `cmd.SetOut` and `cmd.SetErr` to `bytes.Buffer` for testable output.
