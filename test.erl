-module(test).
-export([double/2, say_something/2, threat_t/0, ping/2 , pong/0]).

double(X, Y)->
	2 * X * Y.

say_something(What, 0)->
	done;
	
say_something(What, Times)->
	io:format("~p~n", [What]),
	say_something(What, Times - 1).

ping(0, Pong_pid) ->
	Pong_pid ! finished,
	io:format("ping finished~n", []);
	
ping(N, Pong_pid)->
	Pong_pid ! {ping, self()},
	receive 
			pong ->
				io:format("Ping recv Pong~n", [])
	end,
	ping(N - 1, Pong_pid).

pong()->
	receive 
		finished ->
			io:format("finshed~n", []);
		{ping, Ping_pid} ->
			io:format("Pong recv ping ~n", []),
			Ping_pid ! pong,
			pong()
	end.
		
		
		

threat_t()->
	P_pid = spawn(test, pong, []),
	spawn(test, ping, [3, P_pid]).
	%Pid = spawn(test, say_something, [sb, 2]),
	%Pid2 = spawn(test, say_something, [sx, 3]).
