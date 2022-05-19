%%AR GATHERING APPLICATION %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% functionReqs(functionId, listOfSWReqs, HWReqs(memory, vCPU, Htz), listOfServiceReqs(serviceType, latency))
functionReqs(fCheck, [py3], (512, 2, 500), [(database, 200)]).
functionReqs(fBuyOrSell, [py3], (2048, 4, 1200), []).
functionReqs(fSell, [js, py3], (256, 2, 400), []).
functionReqs(fBuy, [js, py3], (256, 2, 400), []).
functionReqs(fRecord, [py3], (1600, 2, 500), [(database, 200)]).

%functionBehaviour(functionId, listOfInputs, listOfun(serviceReq, TypeParam), listOfOutputs)
functionBehaviour(fCheck, [Stock, Value],[Stock],[Stock, Value]).
functionBehaviour(fBuyOrSell, [Stock, Value],[],[Stock, Value]).
functionBehaviour(fSell, [Stock, Value],[],[Stock, Value]).
functionBehaviour(fBuy, [Stock, Value],[],[Stock, Value]).
functionBehaviour(fRecord, [_, Value],[],[Value]).     

%functionOrch(functionOrchId, operatorId, triggeringEvent(eventSource, eventType, inputParameters), (latency from source, dest)
%               listOfFunctions(functionId(listOfServiceInstances), latencyFromPrevious)

functionOrch(
  stockOrch,(event2, [top,low,medium]), %trigger
  seq(
    fun(fCheck,[],250),
    seq(
      if(
          fun(fBuyOrSell,[],150),
          fun(fSell,[],105),
          fun(fBuy,[],180)
      ),
      fun(fRecord,[],180)
    )
  )
).


% lattice of security types
g_lattice_higherThan(top, medium).
g_lattice_higherThan(medium, low).

% lattice security types color for print, if do not needed use 'latticeColor(_,default).'
latticeColor(low,red).
latticeColor(medium,orange).
latticeColor(top,green).

% node labeling
nodeLabel(NodeId, top)    :- node(NodeId,_,_,SecCaps,_,_), member(antiTamp, SecCaps), member(pubKeyE, SecCaps).
nodeLabel(NodeId, medium) :- node(NodeId,_,_,SecCaps,_,_), \+(member(antiTamp, SecCaps)), member(pubKeyE, SecCaps).
nodeLabel(NodeId, low)    :- node(NodeId,_,_,SecCaps,_,_), \+(member(pubKeyE, SecCaps)).

%service labeling
serviceLabel(SId, _, top) :- service(SId, appOp, _, _).
serviceLabel(SId, _, top) :- service(SId, pa, _, _).
serviceLabel(SId, maps, medium) :- service(SId, cloudProvider, maps, _).
serviceLabel(SId, Type, low) :- 
    service(SId, Provider, Type, _),
    \+(Provider == appOp),
    \+((Provider == cloudProvider, Type == maps)).