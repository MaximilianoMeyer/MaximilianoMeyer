package main

import (
	"fmt"
	"net"
)

func handleClient(conn net.Conn) {
	// lógica de controle do cliente
	fmt.Println("Conexão estabelecida com sucesso:", conn.RemoteAddr())
}

func main() {
	fmt.Println("Aguardando conexão")
	listener, err := net.Listen("tcp", "0.0.0.0:443")
	if err != nil {
		fmt.Println("Erro ao iniciar o servidor:", err)
		return
	}
	defer listener.Close()
	for {
		conn, err := listener.Accept()
		if err != nil {
			fmt.Println("Erro ao aceitar a conexão do cliente:", err)
			continue
		}
		// inicia uma nova goroutine para lidar com o cliente
		go handleClient(conn)
	}
}
