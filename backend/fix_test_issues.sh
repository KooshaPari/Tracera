#!/bin/bash

# Fix agent_handler_test.go - line 326 (err := should be err =)
sed -i '' 's/^\s*err := handler.AssignTask(c)$/\terr = handler.AssignTask(c)/g' internal/handlers/agent_handler_test.go

# Fix agent_handler_test.go - line 873 (err := should be err =)
sed -i '' 's/^\s*err := handler.CreateAgent(c)$/\terr = handler.CreateAgent(c)/g' internal/handlers/agent_handler_test.go

# Fix agent_handler_test.go - line 961 (err := should be err =)
sed -i '' '960,965s/^\s*err := handler.AgentHeartbeat(c)$/\terr = handler.AgentHeartbeat(c)/g' internal/handlers/agent_handler_test.go

# Fix agent_handler_test.go - line 997 (err := should be err =)
sed -i '' '996,1002s/^\s*err := handler.RegisterAgent(c)$/\terr = handler.RegisterAgent(c)/g' internal/handlers/agent_handler_test.go

# Fix agent_handler_test.go - line 1020 (err := should be err =)
sed -i '' '1019,1022s/^\s*err := handler.AgentHeartbeat(c)$/\terr = handler.AgentHeartbeat(c)/g' internal/handlers/agent_handler_test.go

# Fix subscription_manager_test.go - line 83 (err := should be err =)
sed -i '' 's/^\s*err := sm.Unsubscribe(sub.ID)$/\terr = sm.Unsubscribe(sub.ID)/g' internal/websocket/subscription_manager_test.go

echo "Fixes applied"
