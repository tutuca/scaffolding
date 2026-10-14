GOAL
[Describe the finished state in one or two sentences. 
Be specific about what DONE looks like, and make it something you can measure. 

Example: "Every product page in /pages has the new pricing and every link opens."]

WHERE THE WORK IS
[Tell the agent where to look.

Examples: "Scan the /pages folder for files with old pricing." Or "Read TODO.md and treat each unchecked box as a task.

" Or " Check my connected task board for items tagged ai."]

HOW TO WORK
- Do one item at a time. Finish it fully before starting the next.

- When running under the goal-loop skill, tag each item with its role: `sweep`
  for mechanical checks, `plan` for planning, and `vision` for anything that
  reads an image. Record the actual model and, if the harness has one, the
  reasoning effort from that skill's routing table after checking the available
  models.

- Match the patterns you find in existing files. Do not invent new ones.

- If an item needs a decision only I can make (spending money, deleting things, emailing a person), stop on that item, add it to a "needs me" list, and move to the next one.

HOW TO CHECK YOURSELF
After each item, prove it is done before you mark it done.

[Pick what fits: "run the tests" / "re-read the file and confirm it meets the goal" / "open the link and confirm it loads." Checking means evidence, not confidence.]

If the check fails, fix it and check again. Three tries per item, then log it as blocked and move on.

HOW TO REMEMBER
Keep your state at tmp/goals/<slug>/LOOP-STATE.md - one file per goal, in the goal's
own directory, with the objective and returned goal identifier (if present), or
"inline", in its first lines. Only create a persistent goal when explicitly
requested; otherwise use this checklist inline. Several of these loops run at
once, and each writing its own file is what keeps them from writing over each
other; keep your probes, crops and logs in that same directory for the same reason.

After each item, write the item name, its status (done / blocked / needs me), what you changed, and anything the next run should know.

Read this file FIRST every run so you never redo finished work.

Stage only the paths you changed when you commit (git add <paths>, never git add
-A): another loop's unfinished work is in the tree, and a sweep would commit it
under your message. Never run git checkout ., git reset --hard or git stash here.

WHEN TO STOP
Finish only when the objective is achieved and no required items remain.
Logged blockers do not count as completion; keep taking independent work.
For a persistent goal, follow the goal skill's lifecycle rules for completion,
blocking and an explicit pause request. For inline work, respect any requested
item limit and report remaining work without marking it complete.

Then give me a short report: what got done, what is blocked, what needs my call.

Start by reading your goal's LOOP-STATE.md if it exists, then find the work.
