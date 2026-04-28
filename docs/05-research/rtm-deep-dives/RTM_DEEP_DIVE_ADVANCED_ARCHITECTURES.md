# Requirements Traceability - Deep Dive: Advanced Architectures

## Microservices & Distributed Systems

### Challenge: Cross-Service Traceability

In microservices architectures, requirements span multiple services:

```
User Story: "User can checkout"
    ↓ (decomposes_to)
├─ Cart Service: "Add items to cart"
├─ Inventory Service: "Check stock availability"
├─ Payment Service: "Process payment"
├─ Order Service: "Create order"
└─ Notification Service: "Send confirmation"
```

### Event Sourcing for Traceability

```python
class RequirementEvent:
    """Base class for requirement events"""
    event_id: str
    requirement_id: str
    timestamp: datetime
    user: str

class RequirementCreated(RequirementEvent):
    data: Requirement

class RequirementUpdated(RequirementEvent):
    old_data: Requirement
    new_data: Requirement
    changes: dict

class LinkCreated(RequirementEvent):
    link: Link

class RequirementEventStore:
    def __init__(self):
        self.events: List[RequirementEvent] = []
    
    def append(self, event: RequirementEvent):
        """Append event to store"""
        self.events.append(event)
        self.publish_event(event)  # Publish to event bus
    
    def get_events(self, requirement_id: str) -> List[RequirementEvent]:
        """Get all events for a requirement"""
        return [e for e in self.events if e.requirement_id == requirement_id]
    
    def rebuild_state(self, requirement_id: str) -> Requirement:
        """Rebuild requirement state from events"""
        events = self.get_events(requirement_id)
        state = None
        
        for event in events:
            if isinstance(event, RequirementCreated):
                state = event.data
            elif isinstance(event, RequirementUpdated):
                state = event.new_data
        
        return state
```

### Distributed Traceability with Kafka

```python
from kafka import KafkaProducer, KafkaConsumer
import json

class DistributedTraceability:
    def __init__(self, kafka_brokers: List[str]):
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.consumer = KafkaConsumer(
            'requirement-events',
            bootstrap_servers=kafka_brokers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
    
    def publish_requirement_change(self, event: RequirementEvent):
        """Publish requirement change to all services"""
        self.producer.send('requirement-events', {
            'event_type': type(event).__name__,
            'requirement_id': event.requirement_id,
            'timestamp': event.timestamp.isoformat(),
            'data': event.data
        })
    
    def subscribe_to_changes(self, callback):
        """Subscribe to requirement changes"""
        for message in self.consumer:
            event = message.value
            callback(event)
```

### Service Mesh Traceability

Using service mesh (Istio, Linkerd) for distributed tracing:

```yaml
# Istio VirtualService with traceability headers
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: requirement-service
spec:
  hosts:
  - requirement-service
  http:
  - match:
    - headers:
        x-requirement-id:
          regex: ".*"
    route:
    - destination:
        host: requirement-service
      headers:
        request:
          add:
            x-trace-requirement: "%REQ(x-requirement-id)%"
```

## MBSE (Model-Based Systems Engineering)

### SysML Integration

```python
class SysMLRequirement:
    """SysML requirement representation"""
    id: str
    text: str
    stereotype: str  # <<requirement>>, <<functionalRequirement>>, etc.
    satisfy: List[str]  # IDs of design elements that satisfy this
    verify: List[str]  # IDs of test cases that verify this
    refine: List[str]  # IDs of refined requirements
    derive: List[str]  # IDs of derived requirements
    trace: List[str]  # IDs of traced elements

class SysMLTraceability:
    def __init__(self):
        self.requirements: Dict[str, SysMLRequirement] = {}
    
    def import_from_sysml(self, model_path: str):
        """Import requirements from SysML model"""
        # Parse XMI or other SysML format
        model = self.parse_sysml_model(model_path)
        
        for req in model.requirements:
            self.requirements[req.id] = SysMLRequirement(
                id=req.id,
                text=req.text,
                stereotype=req.stereotype,
                satisfy=req.satisfy_relationships,
                verify=req.verify_relationships,
                refine=req.refine_relationships,
                derive=req.derive_relationships,
                trace=req.trace_relationships
            )
    
    def export_to_rtm(self) -> List[Requirement]:
        """Export to RTM system"""
        rtm_requirements = []
        
        for sysml_req in self.requirements.values():
            req = Requirement(
                id=sysml_req.id,
                title=self.extract_title(sysml_req.text),
                description=sysml_req.text,
                type=self.map_stereotype(sysml_req.stereotype)
            )
            rtm_requirements.append(req)
        
        return rtm_requirements
```

### Cameo/MagicDraw Integration

```python
class CameoIntegration:
    def __init__(self, api_endpoint: str):
        self.api = CameoAPI(api_endpoint)
    
    def sync_requirements(self):
        """Bidirectional sync with Cameo"""
        # Pull from Cameo
        cameo_reqs = self.api.get_requirements()
        
        for cameo_req in cameo_reqs:
            # Check if exists in RTM
            rtm_req = self.rtm.get_requirement(cameo_req.id)
            
            if not rtm_req:
                # Create in RTM
                self.rtm.create_requirement(self.convert_from_cameo(cameo_req))
            elif rtm_req.updated_at < cameo_req.updated_at:
                # Update from Cameo
                self.rtm.update_requirement(self.convert_from_cameo(cameo_req))
            elif rtm_req.updated_at > cameo_req.updated_at:
                # Push to Cameo
                self.api.update_requirement(self.convert_to_cameo(rtm_req))
```

## Blockchain for Immutable Traceability

### Smart Contract for Requirements

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract RequirementTraceability {
    struct Requirement {
        string id;
        string title;
        string description;
        string status;
        uint256 createdAt;
        uint256 updatedAt;
        address owner;
    }
    
    struct Link {
        string sourceId;
        string targetId;
        string linkType;
        uint256 createdAt;
    }
    
    mapping(string => Requirement) public requirements;
    mapping(string => Link[]) public links;
    
    event RequirementCreated(string id, address owner, uint256 timestamp);
    event RequirementUpdated(string id, address updater, uint256 timestamp);
    event LinkCreated(string sourceId, string targetId, string linkType, uint256 timestamp);
    
    function createRequirement(
        string memory id,
        string memory title,
        string memory description
    ) public {
        require(bytes(requirements[id].id).length == 0, "Requirement already exists");
        
        requirements[id] = Requirement({
            id: id,
            title: title,
            description: description,
            status: "draft",
            createdAt: block.timestamp,
            updatedAt: block.timestamp,
            owner: msg.sender
        });
        
        emit RequirementCreated(id, msg.sender, block.timestamp);
    }
    
    function createLink(
        string memory sourceId,
        string memory targetId,
        string memory linkType
    ) public {
        require(bytes(requirements[sourceId].id).length > 0, "Source requirement not found");
        require(bytes(requirements[targetId].id).length > 0, "Target requirement not found");
        
        links[sourceId].push(Link({
            sourceId: sourceId,
            targetId: targetId,
            linkType: linkType,
            createdAt: block.timestamp
        }));
        
        emit LinkCreated(sourceId, targetId, linkType, block.timestamp);
    }
    
    function getRequirement(string memory id) public view returns (Requirement memory) {
        return requirements[id];
    }
    
    function getLinks(string memory sourceId) public view returns (Link[] memory) {
        return links[sourceId];
    }
}
```

### Hyperledger Fabric for Enterprise

```python
from hfc.fabric import Client

class FabricTraceability:
    def __init__(self, network_config: str):
        self.client = Client(net_profile=network_config)
        self.channel = self.client.new_channel('requirement-channel')
    
    async def create_requirement(self, req: Requirement):
        """Create requirement on blockchain"""
        response = await self.client.chaincode_invoke(
            requestor=self.user,
            channel_name='requirement-channel',
            peers=['peer0.org1.example.com'],
            args=[req.id, req.title, req.description],
            cc_name='requirement-chaincode',
            fcn='createRequirement'
        )
        return response
    
    async def query_requirement_history(self, req_id: str):
        """Query complete history from blockchain"""
        response = await self.client.chaincode_query(
            requestor=self.user,
            channel_name='requirement-channel',
            peers=['peer0.org1.example.com'],
            args=[req_id],
            cc_name='requirement-chaincode',
            fcn='getRequirementHistory'
        )
        return response
```

## Knowledge Graph with Ontologies

### OWL Ontology for Requirements

```turtle
@prefix req: <http://example.org/requirements#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Classes
req:Requirement a owl:Class .
req:Epic rdfs:subClassOf req:Requirement .
req:Feature rdfs:subClassOf req:Requirement .
req:UserStory rdfs:subClassOf req:Requirement .
req:TestCase a owl:Class .
req:CodeArtifact a owl:Class .

# Properties
req:decomposesTo a owl:ObjectProperty ;
    rdfs:domain req:Requirement ;
    rdfs:range req:Requirement .

req:implements a owl:ObjectProperty ;
    rdfs:domain req:CodeArtifact ;
    rdfs:range req:Requirement .

req:tests a owl:ObjectProperty ;
    rdfs:domain req:TestCase ;
    rdfs:range req:Requirement .

# Data Properties
req:hasTitle a owl:DatatypeProperty ;
    rdfs:domain req:Requirement ;
    rdfs:range xsd:string .

req:hasStatus a owl:DatatypeProperty ;
    rdfs:domain req:Requirement ;
    rdfs:range xsd:string .
```

### SPARQL Queries for Traceability

```sparql
# Find all requirements decomposed from an epic
PREFIX req: <http://example.org/requirements#>

SELECT ?child ?title
WHERE {
  req:EPIC-001 req:decomposesTo+ ?child .
  ?child req:hasTitle ?title .
}

# Find untested requirements
SELECT ?req ?title
WHERE {
  ?req a req:Requirement ;
       req:hasTitle ?title .
  FILTER NOT EXISTS {
    ?test req:tests ?req .
  }
}

# Find requirements with no implementation
SELECT ?req ?title
WHERE {
  ?req a req:Requirement ;
       req:hasTitle ?title .
  FILTER NOT EXISTS {
    ?code req:implements ?req .
  }
}
```

## Digital Twin Integration

```python
class DigitalTwinTraceability:
    def __init__(self):
        self.physical_system = PhysicalSystem()
        self.digital_twin = DigitalTwin()
        self.requirements = RequirementStorage()
    
    def link_requirement_to_twin(self, req_id: str, twin_component: str):
        """Link requirement to digital twin component"""
        link = Link(
            source_id=req_id,
            target_id=twin_component,
            link_type="monitors",
            metadata={
                "twin_type": "digital_twin",
                "component": twin_component
            }
        )
        self.requirements.create_link(link)
    
    def verify_requirement_in_twin(self, req_id: str) -> bool:
        """Verify requirement using digital twin simulation"""
        req = self.requirements.get_requirement(req_id)
        twin_component = self.get_linked_twin_component(req_id)
        
        # Run simulation
        simulation_result = self.digital_twin.simulate(
            component=twin_component,
            scenario=req.test_scenario
        )
        
        # Verify against requirement
        return self.verify_result(simulation_result, req.acceptance_criteria)
```

