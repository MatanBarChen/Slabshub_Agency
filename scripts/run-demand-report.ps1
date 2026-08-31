# Nightly demand report for the SlabsHub sales agent.
# Registered in Windows Task Scheduler as "SlabsHub Demand Report" (daily 21:15).
# Runs Claude headless with the demand-report scheduled-task skill.
Set-Location "C:\Users\matan\Desktop\Slabshub Agency"
& claude -p "Read C:\Users\matan\.claude\scheduled-tasks\demand-report\SKILL.md and execute it exactly as written." `
    --model sonnet `
    --allowedTools "Read,Write,Glob,Grep,PushNotification,Bash(git *)" `
    *> "prototype\sales-agent\conversations\demand-report-last-run.log"
