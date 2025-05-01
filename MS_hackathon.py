import os
import time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import json

# --- 사용자 설정 값 ---
# TODO: 여기에 실제 Azure AI Hub 연결 문자열을 입력하세요.
# Azure Portal의 Azure AI Hub 리소스 > Keys and Endpoint 에서 확인 가능
# 예: "azureml://japaneast.api.azureml.ms/mlflow/v1.0/subscriptions/YOUR_SUB_ID/resourceGroups/YOUR_RG/providers/Microsoft.MachineLearningServices/workspaces/YOUR_AI_HUB_NAME"
connection_string = "ENTER_YOUR_CONNECTION_STRING" # 여기에 실제 값 입력

# TODO: 여기에 실제 Agent ID(들)을 리스트 형태로 입력하세요.
#      하나의 Agent ID만 사용 권장 (단순화를 위해)
agent_ids = ["ENTER_YOUR_AGENTS_IDS"] # 여기에 실제 값 입력

# --- 코드 시작 ---

# 설정 값 유효성 검사 (간단히)
if "YOUR_CONNECTION_STRING" in connection_string or not connection_string:
    print("❌ connection_string 값을 실제 Azure AI Hub 연결 문자열로 바꾸어 주세요. 프로그램을 종료합니다.")
    exit()

if not agent_ids or "YOUR_AGENT_ID" in agent_ids:
     print("❌ agent_ids 값을 실제 Agent ID로 바꾸어 주세요. (단일 ID 권장) 프로그램을 종료합니다.")
     exit()

# Step 1: Authenticate and Initialize the Client
try:
    print("⏳ Initializing Azure AI Project Client...")
    # DefaultAzureCredential은 환경 변수, 관리 ID, Azure CLI 로그인 등 다양한 방법으로 자동 인증 시도
    credential = DefaultAzureCredential()
    project_client = AIProjectClient.from_connection_string(
        credential=credential,
        conn_str=connection_string
    )
    print("✅ Client initialized successfully.")
except Exception as e:
    print(f"❌ Error initializing client: {e}")
    print("   (연결 문자열 형식이 올바른지, Azure에 로그인 되어 있는지 확인하세요.)")
    exit()

# Step 2: Retrieve Agent (단일 에이전트 사용 권장)
agent = None
if len(agent_ids) == 1:
    agent_id = agent_ids[0]
    try:
        print(f"⏳ Retrieving agent with ID: {agent_id}...")
        agent = project_client.agents.get_agent(agent_id)
        print(f"✅ Agent retrieved: {agent.name} (ID: {agent.id})")
    except Exception as e:
        print(f"❌ Error retrieving agent with ID '{agent_id}': {e}")
        exit()
else:
    # 여러 에이전트를 동시에 다루는 로직은 복잡하므로, 이 예제에서는 단일 에이전트만 지원
    print("❌ 이 예제 코드는 단일 Agent ID만 지원합니다. agent_ids 리스트를 수정해주세요.")
    exit()

# Step 3: Create a Communication Thread
try:
    print("⏳ Creating communication thread...")
    thread = project_client.agents.create_thread()
    print(f"✅ Communication thread created: {thread.id}")
    print("\n--- 대화 시작 ---")
    print("대화를 종료하려면 'quit' 또는 'exit'을 입력하세요.")
except Exception as e:
    print(f"❌ Error creating thread: {e}")
    exit()

# Step 4: 연속 대화 루프 시작
last_message_timestamp = None # 마지막으로 확인한 메시지 시간을 추적하기 위한 변수

while True:
    try:
        # 사용자 입력 받기
        user_message = input("You: ")

        # 종료 명령어 확인
        if user_message.lower() in ['quit', 'exit']:
            print("대화를 종료합니다.")
            break # 루프 종료

        # 사용자 메시지가 비어 있지 않으면 전송
        if not user_message.strip():
            print("빈 메시지는 전송할 수 없습니다.")
            continue # 다시 입력 받기

        # Step 4.1: Send User Message to the Thread
        print("⏳ Sending user message...")
        sent_message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=user_message # content는 보통 문자열이지만, API 명세 확인 필요
        )
        print(f"✅ User message sent (ID: {sent_message.id}).")

        # Step 4.2: Create and Process Agent Run
        print(f"⏳ Requesting run for agent '{agent.name}'...")
        run = project_client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=agent.id
        )
        print(f"✅ Run created (ID: {run.id}). Starting polling for completion...")

        # Step 4.3: Poll for Run Completion (개선된 부분)
        polling_interval_seconds = 2 # 상태 확인 간격 (초)
        max_wait_seconds = 120 # 최대 대기 시간 (초) - 필요시 조절
        start_time = time.time()

        while run.status in ["not_started", "running", "queued"]:
            if time.time() - start_time > max_wait_seconds:
                print(f"❌ Run timed out after {max_wait_seconds} seconds with status: {run.status}")
                # 타임아웃 시 다음 입력으로 넘어갈지, 종료할지 결정
                break # 루프 탈출 (다음 입력 대기)

            print(f"   Polling run status: {run.status} (Elapsed: {int(time.time() - start_time)}s)")
            time.sleep(polling_interval_seconds)
            try:
                run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
            except Exception as poll_error:
                print(f"   ❌ Error polling run status: {poll_error}")
                # 폴링 중 오류 발생 시 잠시 후 다시 시도하거나 루프 탈출
                time.sleep(polling_interval_seconds * 2) # 잠시 더 대기 후 재시도

        # Check final run status
        if run.status == "completed":
            print(f"✅ Run completed successfully.")
        else:
            print(f"⚠️ Run finished with status: {run.status}. Attempting to retrieve messages anyway.")
            # 실패/취소된 경우라도 메시지가 있을 수 있으므로 일단 시도

        # Step 4.4: Retrieve and Display *New* Messages (개선된 부분)
        print("\n--- Agent Response ---")
        try:
            # 마지막으로 확인한 메시지 시간 이후의 메시지만 가져오도록 시도 (API가 after 파라미터 지원 시)
            # 참고: 모든 SDK/API가 'after' 필터링을 동일하게 지원하지 않을 수 있음.
            #       만약 after 필터링이 없다면, 이전처럼 모든 메시지를 가져와 시간 비교 필요.
            #       list_messages의 파라미터를 확인하세요. (예: order='asc', after=last_message_id 등)
            #       여기서는 after 필터링이 없다고 가정하고, 시간 비교 로직 사용.

            messages_response = project_client.agents.list_messages(thread_id=thread.id, order="asc") # 시간순 정렬 요청

            if hasattr(messages_response, "data") and messages_response.data:
                new_messages_found = False
                for msg in messages_response.data:
                    # 마지막으로 확인한 메시지가 없거나, 현재 메시지가 그 이후에 생성되었고 assistant 역할일 때
                    if (last_message_timestamp is None or msg.created_at > last_message_timestamp) and msg.role == "assistant":
                        sender_prefix = f"🤖 Agent ({agent.name}):"
                        # content 구조 확인 및 처리 (이전 코드와 유사)
                        if msg.content and isinstance(msg.content, list):
                            for content_item in msg.content:
                                if content_item.get("type") == "text":
                                    print(f"{sender_prefix} {content_item.get('text', {}).get('value', '(Empty text content)')}")
                                    new_messages_found = True
                                elif content_item.get("type") == "image_file":
                                     # 예시: 이미지 파일 ID 출력 (실제 이미지 다운로드/표시는 별도 구현 필요)
                                     print(f"{sender_prefix} [Received image file: ID {content_item.get('image_file', {}).get('file_id')}]")
                                     new_messages_found = True
                                # 다른 content type (예: 코드 인터프리터 출력 파일) 처리 로직 추가
                        elif isinstance(msg.content, str):
                             print(f"{sender_prefix} {msg.content}")
                             new_messages_found = True

                        # 현재 메시지를 마지막으로 확인한 메시지로 업데이트 (가장 마지막 assistant 메시지 기준)
                        if new_messages_found:
                             last_message_timestamp = msg.created_at

                if not new_messages_found:
                    print("... (새로운 Agent 응답을 찾지 못했습니다. Run 상태를 확인하세요)")
            else:
                print("... (메시지를 가져올 수 없거나 스레드에 메시지가 없습니다)")

        except Exception as list_error:
            print(f"❌ Error listing/processing messages: {list_error}")

        # 다시 루프 시작 (사용자 입력 대기)

    except KeyboardInterrupt: # Ctrl+C 로 종료 허용
        print("\nKeyboardInterrupt 감지. 대화를 종료합니다.")
        break
    except Exception as loop_error:
        print(f"❌ 대화 루프 중 오류 발생: {loop_error}")
        # 오류 발생 시 루프를 계속할지, 종료할지 결정 (여기서는 계속 진행)
        # break

# 루프 종료 후 실행될 코드
print("\n대화 세션이 종료되었습니다.")
# TODO: 필요하다면 여기서 thread 삭제 등의 정리 작업 수행
# 예:
# try:
#     project_client.agents.delete_thread(thread_id=thread.id)
#     print(f"🗑️ Thread {thread.id} deleted.")
# except Exception as delete_error:
#     print(f"⚠️ Error deleting thread {thread.id}: {delete_error}")