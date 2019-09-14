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
vid_i : [0..MAX_TIMER] init 0; 

view_pi_pi : [0..MAX_TIMER] init 0;
view_pi_pj : [0..MAX_TIMER] init 0;

new_view_id_i_i :[0..MAX_TIMER] init 0;
new_view_id_i_j :[0..MAX_TIMER] init 0;

//V_SYNC ESTA SINCRONIZADA. TODOS AS INFORMACOES QUE SERAO ENVIADAS PARA OS VEICULOS SAO RESETADAS (-> LINHA 99)
[]broadcast_phase & context_i & my_turn & state_i=BROADCAST & inner_state=8 -> 
(inner_state'=8) & (vid_i'=0) & (new_view_id_i_i'=NO_DATA) & (new_view_id_i_j'=NO_DATA) & (view_pi_pi'=0) & (view_pi_pj'=0) &
(turn_token'= turn_token + 1) & (timer_i'=0)  & (end_process'=1); 

//TAREFA 1 - TAREFA RESPONSAVEL PELO ENVIO PERIODICO DE MENSAGENS
//O LIDER INCREMENTA UM VALOR AO SEU VID (-> LINHA 68) 
[]broadcast_phase & context_i & my_turn & state_i=BROADCAST & inner_state=0 & vid_i<MAX_TIMER -> (inner_state'=inner_state+1) & (vid_i'=vid_i+1); 

//ATUALIZA O VALOR DO VID A SUA VISAO (-> LINHA 71)
[]broadcast_phase & context_i & my_turn & state_i=BROADCAST & inner_state=1 -> (turn_token'= turn_token + 1)  & (new_view_id_i_i'= vid_i) & (inner_state'=0); 

//O LIDER ENVIA A MENSAGEM COM A SUA VISAO E O QUE ELE SABE POR OUTRO LIDER (-> LINHA 95 )
[]broadcast_phase & context_i & my_turn & state_i=BROADCAST & vid_i<MAX_TIMER & (inner_state=2)->  
(view_pi_pi'=new_view_id_i_i) & (view_pi_pj'=new_view_id_i_j) & (turn_token'= turn_token + 1) & (inner_state'=2) & (end_process'=0);

//TAREFA 2 - TAREFA RESPONSAVEL PELO RECEBIMENTO DAS MENSAGENS
//TODAS AS MENSAGENS QUE SAO RECEBIDAS SAO ARMAZENADAS ENQUANTO O TEMPO FOR < TIMEOUT (-> LINHA 104) 
[]wait_phase & context_i & my_turn & state_i=WAIT & timer_i<timeout & inner_state=0 & view_pi_pj>=0 & view_pj_pi>=0 
-> (1-packet_loss_rate):(new_view_id_i_j'=vid_j) & (view_pi_pj'=vid_j) & (timer_i'=timer_i+1) & (turn_token'= turn_token + 1) & (inner_state'=0) & (end_process'=0)
+ (packet_loss_rate): (timer_i'=timer_i+1) & (turn_token'= turn_token + 1) & (inner_state'=0) & (end_process'=0);

//= TIMEOUT. 
//TODAS AS MENSAGENS QUE SAO RECEBIDAS SAO ARMAZENADAS ENQUANTO O TEMPO FOR < TIMEOUT (-> LINHA 110) 
[]wait_phase & context_i & my_turn & state_i=WAIT & timer_i=timeout & inner_state=0 & view_pi_pj>=0 & view_pj_pi>=0 
-> (1-packet_loss_rate):(new_view_id_i_j'=vid_j) & (view_pi_pj'=vid_j) & (turn_token'= turn_token + 1) & (inner_state'=0) & 
(end_process'=2) + (packet_loss_rate): (turn_token'= turn_token + 1) & (inner_state'=0) & (end_process'=2); 

endmodule

module change_state
SYNCHRONIZED : bool init SYNC;	
//PREPARANDO PARA ENVIAR A MENSAGEM (-> LINHA 71)
[] new_phase & phase_token=0 & inner_state=0
-> (turn_token'=0) & (inner_state'=2);

// MUDANCA DA FASE BROADCAST PARA FASE DE ESPERA (-> LINHA 76 SE > TIMEOUT, LINHA 82 SE = TIMEOUT)
[] new_phase & phase_token=0 & inner_state=2 & end_process=0
-> (phase_token'=phase_token+1) & (inner_state'=0) & (state_i'=WAIT) & (state_j'=WAIT) & (turn_token'=0);

// PRERANDO O LIDER PARA ENVIAR A MENSAGEM NOVAMENTE (-> LINHA 64)
[] new_phase & phase_token=0 & inner_state=8  & end_process=1 
-> (phase_token'=0) & (inner_state'=0)  & (state_i'=BROADCAST) 
& (state_j'=BROADCAST) & (turn_token'=0); 

// MUDANCA DA FASE ESPERA PARA FASE DE BROADCAST (-> LINHA 65 )
[] new_phase & phase_token=1 & inner_state=0 & end_process=0 
-> (phase_token'=phase_token-1) & (inner_state'=0)  & (state_i'=BROADCAST) 
& (state_j'=BROADCAST) & (turn_token'=0); 

//TAREFA 3
//MANUTENCAO DAS VISOES (SE ESTIVER SINCRONIZADO (-> LINHA 127)
[] new_phase & phase_token=1 & end_process=2 & state_i=WAIT & state_j = WAIT
& timer_i=timeout & inner_state=0 & view_pi_pj=view_pj_pj & view_pj_pi=view_pi_pi
-> (SYNCHRONIZED'=true) & (inner_state'=inner_state+8); 

//MANUTENCAO DAS VISOES (SE ESTIVER SINCRONIZADO (-> linha 121)
[] new_phase & phase_token=1 & end_process=2 & state_i=WAIT & state_j = WAIT 
& timer_i=timeout & inner_state=0 & (view_pi_pj!=view_pj_pj | view_pj_pi!=view_pi_pi)
-> (SYNCHRONIZED'=false) & (inner_state'=inner_state+8);

//V_SYNC SINCRONIZADA (MUDANCA DE FASE PARA LIMPEZA DOS DADOS QUE SERAO ENVIADOS PARA OUTROS LIDERES -> LINHA 59)
[] new_phase & phase_token=1 & end_process=2 & state_i=WAIT & state_j = WAIT 
& timer_i=timeout & (SYNCHRONIZED=false) &  inner_state=8
-> (phase_token'=phase_token-1) & (inner_state'=8)  & (state_i'=BROADCAST) 
& (state_j'=BROADCAST) & (turn_token'=0) & (end_process'=end_process-1); 

//V_SYNC SINCRONIZADA (MUDANCA DE FASE PARA LIMPEZA DOS DADOS QUE SERAO ENVIADOS PARA OUTROS LIDERES -> LINHA 59)
[] new_phase & phase_token=1 & end_process=2 & state_i=WAIT & state_j = WAIT 
& timer_i=timeout & (SYNCHRONIZED=true) &  inner_state=8
-> (phase_token'=phase_token-1) & (inner_state'=8)  & (state_i'=BROADCAST) 
& (state_j'=BROADCAST) & (turn_token'=0) & (end_process'=end_process-1); 

endmodule

//MODEL RENAMING
module node_j=node_i[N1=N2,state_i=state_j,timer_i=timer_j,context_i=context_j,vid_i=vid_j,new_view_id_i_i=new_view_id_j_j,new_view_id_i_j=new_view_id_j_i,
view_pi_pi=view_pj_pj,view_pi_pj=view_pj_pi]
endmodule
