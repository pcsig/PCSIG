//create by Cleber Brito Santos em 29/05/2019

dtmc

const int timeout;
const double packet_loss_rate;

const MAX_TIMER =80;

const N = 2; 		// Number of leaders
const N1 = 0; 		// Value that identifies the platoon leader
const N2 = 1; 		

const bool node_i_is_platoon = true;			// Indicates the application used by the group
const bool node_j_is_platoon = true;					

global context_i : bool init node_i_is_platoon;		// Indicates the application used by the group
global context_j : bool init node_j_is_platoon;

const BROADCAST = 0;
const WAIT = 1;

const NO_DATA = 0;
const DATA_OK = 1;

//Data constants
const bool SYNC = false;	

global state_i : [0..1] init BROADCAST; // phases that the leader may be
global state_j : [0..1] init BROADCAST; 

const max_needed_inner_states = 8;
const phase_token_max = 1; // token to indicate whose turn it is

const to_end = 2;
global end_process : [0..to_end] init 0;

global phase_token : [0..phase_token_max] init 0;
global turn_token : [0..N] init 0;
global inner_state : [0..max_needed_inner_states] init 0;

formula new_phase = turn_token = N;
formula my_turn = (turn_token=N1);
formula wait_phase = mod(phase_token,2) = 1;
formula broadcast_phase = mod(phase_token,2) = 0;

module node_i

timer_i : [0..timeout] init 0; //message timeout
counter : [0..MAX_TIMER] init 0; 

//SYNCHRONIZED_i : bool init SYNC;	

view_pi_pi : [0..MAX_TIMER] init 0;
view_pi_pj : [0..MAX_TIMER] init 0;

new_view_id_i_i :[0..MAX_TIMER] init 0;
new_view_id_i_j :[0..MAX_TIMER] init 0;

//RESET OF CLOCKS - PART 2
[]broadcast_phase & context_i & my_turn & state_i=BROADCAST & inner_state=8 -> 
(inner_state'=8) & (counter'=0) & (new_view_id_i_i'=NO_DATA) & (new_view_id_i_j'=NO_DATA) & (view_pi_pi'=0) & (view_pi_pj'=0) &
(turn_token'= turn_token + 1) & (timer_i'=0)  & (end_process'=1); 

//TASK 1
//THERE WAS A CHANGE OF VIEW A VALUE WAS INCREMENTED IN 
[]broadcast_phase & context_i & my_turn & state_i=BROADCAST & inner_state=0 & counter<MAX_TIMER -> (inner_state'=inner_state+1) & (counter'=counter+1); 

//PUT THE VIEW IN MACRO VIEW
[]broadcast_phase & context_i & my_turn & state_i=BROADCAST & inner_state=1 -> (turn_token'= turn_token + 1)  & (new_view_id_i_i'= counter) & (inner_state'=0); 

//THE LEADER SEND MESSAGE
[]broadcast_phase & context_i & my_turn & state_i=BROADCAST & counter<MAX_TIMER & (inner_state=2)->  
(view_pi_pi'=new_view_id_i_i) & (view_pi_pj'=new_view_id_i_j) & (turn_token'= turn_token + 1) & (inner_state'=2) & (end_process'=0);

//PHASE WAIT
//< TASK 2
//THE DESTINATION LEADER WILL ADD TO YOUR MACRO VISION IF 
[]wait_phase & context_i & my_turn & state_i=WAIT & timer_i<timeout & inner_state=0 & view_pi_pj>=0 & view_pj_pi>=0 
-> (1-packet_loss_rate):(new_view_id_i_j'=send_timer_2) & (view_pi_pj'=send_timer_2) & (timer_i'=timer_i+1) & (turn_token'= turn_token + 1) & (inner_state'=0) 
+ (packet_loss_rate): (timer_i'=timer_i+1) & (turn_token'= turn_token + 1) & (inner_state'=0);

//= TIMEOUT. 
//THE DESTINATION LEADER WILL ADD TO YOUR MACRO VIEW IF 
[]wait_phase & context_i & my_turn & state_i=WAIT & timer_i=timeout & inner_state=0 & view_pi_pj>=0 & view_pj_pi>=0 
-> (1-packet_loss_rate):(new_view_id_i_j'=send_timer_2) & (view_pi_pj'=send_timer_2) & (turn_token'= turn_token + 1) & (inner_state'=0) & 
(end_process'=2) + (packet_loss_rate): (turn_token'= turn_token + 1) & (inner_state'=0) & (end_process'=2); 

endmodule

module change_state
SYNCHRONIZED : bool init SYNC;	

[] new_phase & phase_token=0 & inner_state=0
-> (turn_token'=0) & (inner_state'=2);

// change the ALL states from BROADCAST TO WAIT
[] new_phase & phase_token=0 & inner_state=2
-> (phase_token'=phase_token+1) & (inner_state'=0) & (state_i'=WAIT) & (state_j'=WAIT) & (turn_token'=0);

// change the ALL states from BROADCAST TO WAIT - RESET
[] new_phase & phase_token=0 & inner_state=8  & end_process=1 
-> (phase_token'=0) & (inner_state'=0)  & (state_i'=BROADCAST) 
& (state_j'=BROADCAST) & (turn_token'=0); //line 66

// change the ALL states from WAIT TO BROADCAST 
[] new_phase & phase_token=1 & end_process=0 
-> (phase_token'=phase_token-1) & (inner_state'=0)  & (state_i'=BROADCAST) 
& (state_j'=BROADCAST) & (turn_token'=0); //line 66

//TASK 3
[] new_phase & phase_token=1 & end_process=2 & state_i=WAIT & state_j = WAIT
& timer_i=timeout & inner_state=0 & view_pi_pj=view_pj_pj & view_pj_pi=view_pi_pi
-> (SYNCHRONIZED'=true) & (inner_state'=inner_state+8); 

[] new_phase & phase_token=1 & end_process=2 & state_i=WAIT & state_j = WAIT 
& timer_i=timeout & inner_state=0 & view_pi_pj!=view_pj_pj & view_pj_pi!=view_pi_pi
-> (SYNCHRONIZED'=false) & (inner_state'=inner_state+8);

[] new_phase & phase_token=1 & end_process=2 & state_i=WAIT & state_j = WAIT 
& timer_i=timeout & (SYNCHRONIZED=false) &  inner_state=8
-> (phase_token'=phase_token-1) & (inner_state'=8)  & (state_i'=BROADCAST) 
& (state_j'=BROADCAST) & (turn_token'=0) & (end_process'=end_process-1); 

[] new_phase & phase_token=1 & end_process=2 & state_i=WAIT & state_j = WAIT 
& timer_i=timeout & (SYNCHRONIZED=true) &  inner_state=8
-> (phase_token'=phase_token-1) & (inner_state'=8)  & (state_i'=BROADCAST) 
& (state_j'=BROADCAST) & (turn_token'=0) & (end_process'=end_process-1); 

endmodule

//MODEL RENAMING
module node_j=node_i[N1=N2,state_i=state_j,timer_i=timer_2,context_i=context_j,counter=send_timer_2,new_view_id_i_i=new_view_id_j_j,new_view_id_i_j=new_view_id_j_i,
view_pi_pi=view_pj_pj,view_pi_pj=view_pj_pi,SYNCHRONIZED_i=SYNCHRONIZED_2]
endmodule
