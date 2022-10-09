
struct St_Query_Rsp {
    1:required bool status,
    2:optional string msg,
    5:optional string error
}
struct St_Query_Req {
    1:required string method_name,
    2:required binary params,
	3:required string token
}
service TestService {
    string echo(1:string param),
    St_Query_Rsp query(1:St_Query_Req rsp),    
    St_Query_Rsp auth(1:string username, 2:string password, 5:bool compress, 8:string mac, 10:string version),
    St_Query_Rsp auth_by_token(1: string username, 2:string token),
    St_Query_Rsp login(1:string username, 2:string password, 8:string mac, 10:string version)
}