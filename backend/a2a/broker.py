"""
Agent-to-Agent (A2A) messaging broker using Azure Service Bus
"""

import asyncio
import json
import logging
from typing import Dict, Callable, Optional, List, Any
from uuid import uuid4
from datetime import datetime, timedelta
import concurrent.futures

from common.schemas import A2AMessage, A2AResponse, AgentType, MessageStatus
from common.config import get_settings

# Try to import Azure Service Bus, fallback to mock for local dev
try:
    from azure.servicebus import ServiceBusClient, ServiceBusMessage
    from azure.servicebus.aio import ServiceBusClient as AsyncServiceBusClient
    from azure.servicebus.aio import ServiceBusReceiver, ServiceBusSender
    from azure.core.credentials import AccessToken
    from common.auth import get_credential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Azure Service Bus not available, using mock broker for local development")

logger = logging.getLogger(__name__)


class AsyncCredentialWrapper:
    """Wrapper to make synchronous credentials work with async Service Bus clients."""
    
    def __init__(self, credential):
        self._credential = credential
    
    async def get_token(self, *scopes, **kwargs) -> AccessToken:
        """Get token asynchronously using thread pool."""
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            token = await loop.run_in_executor(
                executor, 
                self._credential.get_token, 
                *scopes
            )
        return token


class MockA2ABroker:
    """Mock A2A broker for local development without Azure Service Bus."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        logger.info(f"Initialized Mock A2A Broker for agent: {agent_name}")
    
    async def publish(self, message: A2AMessage) -> bool:
        """Mock publish - just log the message."""
        logger.info(f"Mock publish from {self.agent_name}: {message.intent}")
        return True
    
    async def start_listening(self):
        """Mock listener - just log."""
        logger.info(f"Mock A2A listener started for agent: {self.agent_name}")
        # Keep the task alive but don't actually listen
        while True:
            await asyncio.sleep(60)
    
    def register_handler(self, message_type: str, handler: Callable):
        """Mock register handler."""
        logger.info(f"Mock handler registered for {message_type}")
    
    async def close(self):
        """Mock close."""
        logger.info(f"Mock A2A broker closed for agent: {self.agent_name}")


class A2ABroker:
    """Agent-to-Agent messaging broker using Azure Service Bus."""
    
    def __init__(self, agent_name: str):
        self.settings = get_settings()
        self.agent_name = agent_name
        
        # Map agent names to agent types
        agent_type_map = {
            "orchestrator": AgentType.ORCHESTRATOR,
            "nl2sql-agent": AgentType.NL2SQL,
            "vector-agent": AgentType.VECTOR,
            "api-agent": AgentType.API,
            "frontend": AgentType.FRONTEND,
        }
        
        self.agent_type = agent_type_map.get(agent_name.lower(), AgentType.API)
        
        # Message tracking for idempotency
        self._processed_messages: Dict[str, datetime] = {}
        self._message_handlers: Dict[str, Callable] = {}
        
        # Azure Service Bus clients
        self._client: Optional[AsyncServiceBusClient] = None
        self._sender: Optional[ServiceBusSender] = None
        self._receiver: Optional[ServiceBusReceiver] = None
        
    async def _get_client(self) -> AsyncServiceBusClient:
        """Get or create Azure Service Bus client."""
        if self._client is None:
            # Use credential-based authentication (AAD) as SAS is disabled
            credential = get_credential()
            
            # Wrap the credential to make it async-compatible
            async_credential = AsyncCredentialWrapper(credential)
            
            # Use just the namespace without https:// prefix for FQDN
            fully_qualified_namespace = self.settings.service_bus_namespace
            if fully_qualified_namespace.startswith("https://"):
                fully_qualified_namespace = fully_qualified_namespace.replace("https://", "")
            
            logger.info(f"Connecting to Service Bus using AAD credentials: {fully_qualified_namespace}")
            
            try:
                self._client = AsyncServiceBusClient(
                    fully_qualified_namespace=fully_qualified_namespace,
                    credential=async_credential
                )
                logger.info("✓ Service Bus client created successfully with AAD authentication")
            except Exception as e:
                logger.error(f"Failed to create Service Bus client with AAD: {e}")
                raise
        return self._client
    
    async def _get_sender(self) -> ServiceBusSender:
        """Get or create message sender."""
        if self._sender is None:
            client = await self._get_client()
            self._sender = client.get_topic_sender(
                topic_name=self.settings.service_bus_topic
            )
        return self._sender
    
    async def _get_receiver(self) -> ServiceBusReceiver:
        """Get or create message receiver for this agent."""
        if self._receiver is None:
            client = await self._get_client()
            subscription_name = f"{self.settings.service_bus_subscription_prefix}{self.agent_name}"
            self._receiver = client.get_subscription_receiver(
                topic_name=self.settings.service_bus_topic,
                subscription_name=subscription_name,
                max_wait_time=5
            )
        return self._receiver
    
    def _is_message_processed(self, message_id: str) -> bool:
        """Check if message has already been processed (idempotency)."""
        if message_id in self._processed_messages:
            # Clean up old entries (older than 1 hour)
            cutoff = datetime.utcnow() - timedelta(hours=1)
            self._processed_messages = {
                k: v for k, v in self._processed_messages.items()
                if v > cutoff
            }
            return message_id in self._processed_messages
        return False
    
    def _mark_message_processed(self, message_id: str):
        """Mark message as processed."""
        self._processed_messages[message_id] = datetime.utcnow()
    
    async def publish(self, message: A2AMessage) -> bool:
        """Publish message to Service Bus topic."""
        try:
            logger.info(f"🚀 ATTEMPTING TO PUBLISH MESSAGE:")
            logger.info(f"   Message ID: {message.message_id}")
            logger.info(f"   From Agent: {message.from_agent}")
            logger.info(f"   To Agents: {message.to_agents}")
            logger.info(f"   Intent: {message.intent}")
            logger.info(f"   Payload: {message.payload}")
            
            sender = await self._get_sender()
            logger.info(f"✅ Got Service Bus sender successfully")
            
            # Serialize message
            message_body = message.model_dump_json()
            logger.info(f"📦 Serialized message body: {message_body[:200]}...")
            
            service_bus_message = ServiceBusMessage(
                body=message_body,
                message_id=message.message_id,
                correlation_id=message.correlation_id,
                content_type="application/json"
            )
            
            # Add routing properties for subscription filters
            service_bus_message.application_properties = {
                "intent": message.intent.value,
                "from_agent": message.from_agent.value,
                "to_agents": ",".join([agent.value for agent in message.to_agents])  # Convert list to comma-separated string
            }
            logger.info(f"🏷️  Application properties: {service_bus_message.application_properties}")
            
            await sender.send_messages(service_bus_message)
            logger.info(f"✅ SUCCESSFULLY PUBLISHED message {message.message_id} for intent {message.intent}")
            return True
            
        except Exception as e:
            logger.error(f"❌ FAILED TO PUBLISH message {message.message_id}: {e}")
            import traceback
            logger.error(f"❌ FULL TRACEBACK: {traceback.format_exc()}")
            return False
    
    async def publish_response(self, response: A2AResponse) -> bool:
        """Publish response message."""
        try:
            sender = await self._get_sender()
            
            # Serialize response
            response_body = response.model_dump_json()
            service_bus_message = ServiceBusMessage(
                body=response_body,
                message_id=response.message_id,
                correlation_id=response.correlation_id,
                content_type="application/json"
            )
            
            # Add routing properties
            service_bus_message.application_properties = {
                "message_type": "response",
                "from_agent": response.from_agent.value,
                "to_agent": response.to_agent.value,
                "status": response.status.value
            }
            
            await sender.send_messages(service_bus_message)
            logger.info(f"Published response {response.message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish response {response.message_id}: {e}")
            return False
    
    def register_handler(self, intent: str, handler: Callable):
        """Register message handler for specific intent."""
        self._message_handlers[intent] = handler
        logger.info(f"Registered handler for intent: {intent}")
    
    async def _process_message(self, message_body: str) -> Optional[A2AResponse]:
        """Process incoming message and return response if applicable."""
        try:
            # Parse message
            logger.info(f"🔍 PARSING MESSAGE BODY: {message_body[:500]}...")
            message_data = json.loads(message_body)
            logger.info(f"🔍 MESSAGE DATA KEYS: {list(message_data.keys())}")
            logger.info(f"🔍 MESSAGE DATA: {message_data}")
            
            # Handle both regular messages and responses
            if message_data.get("message_type") == "response":
                logger.info(f"📨 Processing as A2AResponse...")
                # This is a response - handle differently
                response = A2AResponse(**message_data)
                await self._handle_response(response)
                return None
            else:
                logger.info(f"📨 Processing as A2AMessage...")
                # Check if this looks like a response by checking for response-specific fields
                if "result" in message_data and "from_agent" in message_data and "to_agent" in message_data:
                    logger.info(f"🔄 Detected response message format, processing as A2AResponse...")
                    response = A2AResponse(**message_data)
                    await self._handle_response(response)
                    return None
                
                # Regular A2A message
                message = A2AMessage(**message_data)
                
                # Check if this agent should process this message
                if self.agent_type not in message.to_agents:
                    return None
                
                # Check idempotency
                if self._is_message_processed(message.message_id):
                    logger.info(f"Message {message.message_id} already processed, skipping")
                    return None
                
                # Find handler for intent
                handler = self._message_handlers.get(message.intent.value)
                if not handler:
                    logger.warning(f"No handler registered for intent: {message.intent}")
                    return A2AResponse(
                        message_id=str(uuid4()),
                        correlation_id=message.correlation_id,
                        from_agent=self.agent_type,
                        to_agent=message.from_agent,
                        status=MessageStatus.ERROR,
                        error=f"No handler for intent: {message.intent}"
                    )
                
                # Process message
                try:
                    result = await handler(message)
                    self._mark_message_processed(message.message_id)
                    
                    return A2AResponse(
                        message_id=str(uuid4()),
                        correlation_id=message.correlation_id,
                        from_agent=self.agent_type,
                        to_agent=message.from_agent,
                        status=MessageStatus.SUCCESS,
                        result=result or {}
                    )
                    
                except Exception as e:
                    logger.error(f"Handler failed for message {message.message_id}: {e}")
                    return A2AResponse(
                        message_id=str(uuid4()),
                        correlation_id=message.correlation_id,
                        from_agent=self.agent_type,
                        to_agent=message.from_agent,
                        status=MessageStatus.ERROR,
                        error=str(e)
                    )
                    
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            return None
    
    async def _handle_response(self, response: A2AResponse):
        """Handle incoming response message."""
        # Store or forward response as needed
        # This could be enhanced to notify waiting coroutines
        logger.info(f"Received response {response.message_id} with status {response.status}")
    
    async def start_listening(self):
        """Start listening for messages (blocking)."""
        logger.info(f"🎧 STARTING MESSAGE LISTENER for agent: {self.agent_name}")
        logger.info(f"🎯 Agent type: {self.agent_type}")
        subscription_name = f"{self.settings.service_bus_subscription_prefix}{self.agent_name}"
        logger.info(f"📝 Subscription name: {subscription_name}")
        
        try:
            logger.info(f"🔗 Getting Service Bus receiver...")
            receiver = await self._get_receiver()
            logger.info(f"✅ Got Service Bus receiver successfully")
            
            async with receiver:
                logger.info(f"🔄 Starting message loop - waiting for messages...")
                async for message in receiver:
                    logger.info(f"📨 RECEIVED MESSAGE!")
                    logger.info(f"   Message ID: {message.message_id}")
                    logger.info(f"   Correlation ID: {message.correlation_id}")
                    logger.info(f"   Body: {str(message)[:200]}...")
                    logger.info(f"   Properties: {message.application_properties}")
                    
                    try:
                        # Process message
                        logger.info(f"⚙️  Processing message...")
                        response = await self._process_message(str(message))
                        logger.info(f"✅ Message processed, response: {response is not None}")
                        
                        # Send response if generated
                        if response:
                            logger.info(f"📤 Sending response...")
                            await self.publish_response(response)
                        
                        # Complete message processing
                        logger.info(f"✅ Completing message processing...")
                        await receiver.complete_message(message)
                        logger.info(f"✅ Message completed successfully")
                        
                    except Exception as e:
                        logger.error(f"❌ Error processing message: {e}")
                        import traceback
                        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
                        # Abandon message for retry
                        await receiver.abandon_message(message)
                        
        except Exception as e:
            logger.error(f"❌ MESSAGE LISTENER FAILED: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            raise
    
    async def close(self):
        """Close Service Bus connections."""
        if self._sender:
            await self._sender.close()
        if self._receiver:
            await self._receiver.close()
        if self._client:
            await self._client.close()


# Utility functions for common messaging patterns
async def send_query_to_agent(
    broker: A2ABroker,
    target_agent: AgentType,
    intent: str,
    payload: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> str:
    """Send query to specific agent and return correlation ID."""
    from common.schemas import A2AMessage, A2AContext, IntentType
    
    message = A2AMessage(
        from_agent=broker.agent_type,
        to_agents=[target_agent],
        intent=IntentType(intent),
        payload=payload,
        context=A2AContext(**(context or {}))
    )
    
    await broker.publish(message)
    return message.correlation_id


async def broadcast_message(
    broker: A2ABroker,
    agents: List[AgentType],
    intent: str,
    payload: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> str:
    """Broadcast message to multiple agents."""
    from common.schemas import A2AMessage, A2AContext, IntentType
    
    message = A2AMessage(
        from_agent=broker.agent_type,
        to_agents=agents,
        intent=IntentType(intent),
        payload=payload,
        context=A2AContext(**(context or {}))
    )
    
    await broker.publish(message)
    return message.correlation_id


def create_broker(agent_name: str):
    """Factory function to create appropriate broker based on environment."""
    settings = get_settings()
    
    logger.info(f"🏭 BROKER FACTORY - Creating broker for agent: {agent_name}")
    logger.info(f"📋 AZURE_AVAILABLE: {AZURE_AVAILABLE}")
    logger.info(f"📋 service_bus_namespace: {bool(settings.service_bus_namespace)}")
    logger.info(f"📋 service_bus_connection_string: {bool(settings.service_bus_connection_string)}")
    
    # Try real Azure Service Bus first if available
    if AZURE_AVAILABLE and (settings.service_bus_namespace or settings.service_bus_connection_string):
        try:
            logger.info(f"🔧 Creating Azure Service Bus broker for agent: {agent_name}")
            broker = A2ABroker(agent_name)
            logger.info(f"✅ Azure Service Bus broker created successfully")
            return broker
        except Exception as e:
            logger.error(f"❌ Failed to create Azure broker: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            logger.warning(f"🔄 Falling back to mock broker")
            return MockA2ABroker(agent_name)
    else:
        logger.warning(f"⚠️  Using Mock A2A Broker - Azure Service Bus not configured (agent: {agent_name})")
        return MockA2ABroker(agent_name)