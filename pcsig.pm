//criado por Cleber Brito Santos em 29/05/2019

dtmc

const int timeout;
const double packet_loss_rate;

const MAX_TIMER =12;

const N = 2; 		// Number of leaders
const N1 = 0; 		// Value that identifies the platoon leader
const N2 = 1; 		

const bool node_1_is_platoon = true;			// Indicates the application used by the group
const bool node_2_is_platoon = true;					

global context_1 : bool init node_1_is_platoon;		// Indicates the application used by the group
global context_2 : bool init node_2_is_platoon;

const BROADCAST = 0;
const WAIT = 1;

const NO_DATA = 0;
const DATA_OK = 1;

//Data constants
const bool SYNC = false;	

global state_1 : [0..1] init BROADCAST; // phases that the leader may be
global state_2 : [0..1] init BROADCAST; 

const max_needed_inner_states = 10;
const phase_token_max = 1; // token to indicate whose turn it is

const to_end = 1;
global end_process : [0..to_end] init 0;

global phase_token : [0..phase_token_max] init 0;
global turn_token : [0..N] init 0;
global inner_state : [0..max_needed_inner_states] init 0;

formula new_phase = turn_token = N;
formula my_turn = (turn_token=N1);
formula wait_phase = mod(phase_token,2) = 1;
formula broadcast_phase = mod(phase_token,2) = 0;

module node_1

timer_1 : [0..timeout] init 0; //message timeout
send_timer_1 : [0..MAX_TIMER] init 0; 

SYNCHRONIZED_1 : bool init SYNC;	

view_p1_p1 : [0..MAX_TIMER] init 0;
view_p1_p2 : [0..MAX_TIMER] init 0;

counter_p1_p1 :[0..MAX_TIMER] init 0;
counter_p1_p2 :[0..MAX_TIMER] init 0;

//RESET OF CLOCKS - PART 2
[]broadcast_phase & context_1 & my_turn & state_1=BROADCAST & inner_state=8 -> 
(inner_state'=8) & (send_timer_1'=0) & (counter_p1_p1'=NO_DATA) & (counter_p1_p2'=NO_DATA) & (view_p1_p1'=0) & (view_p1_p2'=0) &
(turn_token'= turn_token + 1) & (timer_1'=0)  & (end_process'=1);

//BEFORE SENDING THE MESSAGE THE LEADER INCREASES A VALUE TO YOUR COUNTER
[]broadcast_phase & context_1 & my_turn & state_1=BROADCAST & inner_state=0 & send_timer_1<MAX_TIMER -> (inner_state'=inner_state+1) & (send_timer_1'=send_timer_1+1); //soma o contador
//PUT THE VIEW IN MACRO VIEW
[]broadcast_phase & context_1 & my_turn & state_1=BROADCAST & inner_state=1 -> (turn_token'= turn_token + 1)  & (counter_p1_p1'= send_timer_1) & (inner_state'=0); 

//THE LEADER SEND MESSAGE
[]broadcast_phase & context_1 & my_turn & state_1=BROADCAST & send_timer_1<MAX_TIMER & (inner_state=2)->  
(view_p1_p1'=counter_p1_p1) & (view_p1_p2'=counter_p1_p2) & (turn_token'= turn_token + 1) & (inner_state'=2) & (end_process'=0) ;

//PHASE WAIT
//THE DESTINATION LEADER WILL ADD TO YOUR MACRO VISION IF - it receives a message and its view is not contained in the macro view of the message origin leader and vice versa
[]wait_phase & context_1 & my_turn & state_1=WAIT & timer_1<timeout & inner_state=0 & view_p1_p2=0 & view_p2_p1=0 
-> (1-packet_loss_rate):(counter_p1_p2'=send_timer_2) & (view_p1_p2'=send_timer_2) & (timer_1'=timer_1+1) & (turn_token'= turn_token + 1) & (inner_state'=0) 
+ (packet_loss_rate): (timer_1'=timer_1+1) & (turn_token'= turn_token + 1) & (inner_state'=0);

//THE DESTINATION LEADER WILL ADD TO YOUR MACRO VISION IF --- the vision the target leader has about the originator of the message so that the vision of the leader of origin is 0 and the vision of the leader 
//of origin is> = the target leader's view -2
[]wait_phase & context_1 & my_turn & state_1=WAIT & timer_1<timeout & inner_state=0 & view_p1_p2<=counter_p2_p2 & counter_p1_p2>NO_DATA & view_p2_p1>=counter_p1_p1-2
-> (1-packet_loss_rate):(counter_p1_p2'=send_timer_2) & (view_p1_p2'=send_timer_2) & (timer_1'=timer_1+1) & (turn_token'= turn_token + 1) & (inner_state'=0) 
+ (packet_loss_rate): (timer_1'=timer_1+1) & (turn_token'= turn_token + 1) & (inner_state'=0);

//THE DESTINATION LEADER WILL NOT ADD TO YOUR MACRO VISION IF --- the leader of destination does not know anything about him but the leader of origin knows 
//something of the leader of destiny
[]wait_phase & context_1 & my_turn & state_1=WAIT & timer_1<timeout & inner_state=0 & view_p1_p2=0 & view_p2_p1>=1
-> (1):(timer_1'=timer_1+1) & (turn_token'= turn_token + 1) & (inner_state'=0);

//THE DESTINATION LEADER WILL NOT ADD TO YOUR MACRO VISION IF --- the leader of destination knows something about the leader of origin, but the leader of origin 
//does not know anything
[]wait_phase & context_1 & my_turn & state_1=WAIT & timer_1<timeout & inner_state=0 & view_p1_p2>=1 & view_p2_p1=0
-> (1):(timer_1'=timer_1+1) & (turn_token'= turn_token + 1) & (inner_state'=0);

//O LIDER DE DESTINO VAI ADICIONAR AA SUA MACRO VISAO SE --- a visao que o lider de destino tem sobre quem originou a mensagem for < do que a visao do lider de origem e !=0 e
//a visao do lider de origem for >= a visao do lider de destino -2
[]wait_phase & context_1 & my_turn & state_1=WAIT & timer_1<timeout & inner_state=0 & view_p1_p2<=counter_p2_p2 & counter_p1_p2>NO_DATA & view_p2_p1<counter_p1_p1-2
-> (1):(timer_1'=timer_1+1) & (turn_token'= turn_token + 1) & (inner_state'=0);

//o tempo limite para esperar uma nova atualizacao acabou. 
//O LIDER DE DESTINO p1 VAI ADICIONAR AA SUA MACRO VISAO SE --- ele receber uma mensagem e a sua visao nao estiver contida na macro visao do lider de origem da mensagem e vice versa 
[]wait_phase & context_1 & my_turn & state_1=WAIT & timer_1=timeout & inner_state=0 & view_p1_p2=0 & view_p2_p1=0 
-> (1-packet_loss_rate):(counter_p1_p2'=send_timer_2) & (view_p1_p2'=send_timer_2) & (turn_token'= turn_token + 1) & (inner_state'=0) & (SYNCHRONIZED_1'=true) & (end_process'=1)
+ (packet_loss_rate): (turn_token'= turn_token + 1) & (inner_state'=0) & (SYNCHRONIZED_1'=false) & (end_process'=1);

//O LIDER DE DESTINO p1 VAI ADICIONAR AA SUA MACRO VISAO SE --- a visao que o lider de origem tiver sobre o destino for !=0 e < que a visao do lider de destino e o lider de 
//destino tiver a ultima visao enviada pelo lider de origem
[]wait_phase & context_1 & my_turn & state_1=WAIT & timer_1=timeout & inner_state=0 & view_p1_p2<=counter_p2_p2 & counter_p1_p2>NO_DATA & view_p2_p1>=counter_p1_p1-2
-> (1-packet_loss_rate):(counter_p1_p2'=send_timer_2) & (view_p1_p2'=send_timer_2) & (turn_token'= turn_token + 1) & (inner_state'=0) & (SYNCHRONIZED_1'=true) & (end_process'=1)
+ (packet_loss_rate): (turn_token'= turn_token + 1) & (inner_state'=0) & (SYNCHRONIZED_1'=false) & (end_process'=1);

//O LIDER DE DESTINO NAO VAI ADICIONAR AA SUA MACRO VISAO SE --- o lider de destino nao souber nada sobre ele mas o lider de origem souber algo do lider de destino
[]wait_phase & context_1 & my_turn & state_1=WAIT & timer_1=timeout & inner_state=0 & view_p1_p2=0 & view_p2_p1>=1
-> (1):(turn_token'= turn_token + 1) & (inner_state'=0) & (SYNCHRONIZED_1'=false) & (end_process'=1);

//O LIDER DE DESTINO NAO VAI ADICIONAR AA SUA MACRO VISAO SE --- o lider de destino souber alguma coisa sobre o lider de origem, mas o lider de origem nao souber nada
[]wait_phase & context_1 & my_turn & state_1=WAIT & timer_1=timeout & inner_state=0 & view_p1_p2>=1 & view_p2_p1=0
-> (1):(turn_token'= turn_token + 1) & (inner_state'=0) & (SYNCHRONIZED_1'=false) & (end_process'=1);


//O LIDER DE DESTINO VAI ADICIONAR AA SUA MACRO VISAO SE --- a visao que o lider de destino tem sobre quem originou a mensagem for < do que a visao do lider de origem e !=0 e
//a visao do lider de origem for >= a visao do lider de destino -2
[]wait_phase & context_1 & my_turn & state_1=WAIT & timer_1=timeout & inner_state=0 & view_p1_p2<=counter_p2_p2 & counter_p1_p2>NO_DATA & view_p2_p1<counter_p1_p1-2
-> (1):(turn_token'= turn_token + 1) & (inner_state'=0) & (SYNCHRONIZED_1'=false) & (end_process'=1);
endmodule

module change_state

// neste momento o lider vai se preparar para enviar a mensagem
[] new_phase & phase_token=0 & inner_state=0
-> (turn_token'=0) & (inner_state'=2);

// change the ALL states from BROADCAST TO WAIT
[] new_phase & phase_token=0 & inner_state=2
-> (phase_token'=phase_token+1) & (inner_state'=0) & (state_1'=WAIT) & (state_2'=WAIT) & (turn_token'=0);

// change the ALL states from BROADCAST TO WAIT
[] new_phase & phase_token=0 & inner_state=8  & (end_process=0)
-> (phase_token'=phase_token+1) & (inner_state'=0) & (state_1'=WAIT) & (state_2'=WAIT) & (turn_token'=0);

// change the ALL states from BROADCAST TO WAIT - RESET
[] new_phase & phase_token=0 & inner_state=8  & end_process=1 
-> (phase_token'=0) & (inner_state'=0)  & (state_1'=BROADCAST) & (state_2'=BROADCAST) & (turn_token'=0);

// change the ALL states from WAIT TO BROADCAST 
[] new_phase & phase_token=1 & end_process=0 
-> (phase_token'=phase_token-1) & (inner_state'=0)  & (state_1'=BROADCAST) & (state_2'=BROADCAST) & (turn_token'=0); 

//RESET DE TODOS OS RELOGIOS - PARTE 1
[] new_phase & phase_token=1 & end_process=1 & state_1=WAIT & state_2 = WAIT & timer_1=timeout & inner_state=0
-> (phase_token'=phase_token-1) & (inner_state'=inner_state+8)  & (state_1'=BROADCAST) & (state_2'=BROADCAST) & (turn_token'=0) ; 
endmodule

//renomacao dos modulos para diminuir a quantidade de linhas de codigo
module node_2=node_1[N1=N2,state_1=state_2,timer_1=timer_2,context_1=context_2,send_timer_1=send_timer_2,counter_p1_p1=counter_p2_p2,counter_p1_p2=counter_p2_p1,
view_p1_p1=view_p2_p2,view_p1_p2=view_p2_p1,SYNCHRONIZED_1=SYNCHRONIZED_2]
endmodule
