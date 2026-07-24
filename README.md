Este código em MicroPython é um driver/controlador para o sensor de 
energia ACS37800, focado em medir Tensão (V), Corrente (A) e 
Potência Instantânea (W) via barramento de comunicação I2C.

1. Comunicação Básica (read_register e write_register)
Linguagem do Hardware: O sensor transmite dados no padrão
Little Endian (byte menos significativo primeiro).

As duas funções lidam com o envio e recebimento de pacotes de 
32 bits (4 bytes) e gerenciam as chaves de acesso para escrita no chip.

2. Configuração do Sensor (setNumberOfSamples e set_bypass_n_enable)
Desbloqueio: Para alterar parâmetros internos do chip, primeiro
 envia-se um código secreto (ACS37800_CUSTOMER_ACCESS_CODE = 0x4F70656E)
 no registrador de controle (0x2F).

Taxa de Amostragem (setNumberOfSamples): Define quantas amostras internas
o sensor acumula/filtra para gerar os valores (ex: 1023).

Modo Bypass (set_bypass_n_enable): Ativa/desativa o cálculo interno 
por divisor de frequência para obter respostas mais rápidas no sinal.

Preservação de Registradores: O código lê o valor atual antes de alterar
apenas os bits específicos sem apagar outras configurações essenciais (como ganhos ou filtros).

Gravação Volátil vs. Permanente: Permite gravar as alterações na memória
temporária (Shadow) para resposta rápida ou na EEPROM para salvar mesmo se o chip for desligado.

3. Leitura e Conversão Matemáticas (read_instantaneous)
Lê dois registradores voláteis principais e converte os números binários em
valores reais:
Registrador 0x2A (Tensão e Corrente):

16 bits inferiores: Medição de tensão (converte a escala considerando o divisor
de resistores externo 2MΩ / 1.98kΩ).

16 bits superiores: Medição de corrente (converte a escala do sensor ajustada para até 30A).

Registrador 0x2C (Potência):

Lê o valor da potência instantânea e aplica o fator de conversão de escala em mW/W.
