package CircularBufferQueue

type EthereumRawTransaction struct {
	MyIP        string
	FromString  string
	RecipString string
	PeerString 	string
	PeerNameString string
	IpStringSplit string
	IpPort  string
	TimeString string
	TxNonce uint64
	Gprice string
	Glimit uint64
	TxAmount string
	TxPayload string
	TxVString string
	TxRString string
	TxSString string
	TxHash string
}



type FIFOTransactionQueue struct {
	Queue [1000]EthereumRawTransaction
	Tail  int
}

func (f * FIFOTransactionQueue) New() {
	f.Tail = 0
	for counter := 0; counter < 1000; counter ++ {
		f.Queue[counter] = EthereumRawTransaction{
			"",
			"",
			"",
			"",
			"",
			"",
			"",
			"",
			0,
			"",
			0,
			"",
			"",
			"",
			"",
			"",
			"",
		}
	}
}

func (f * FIFOTransactionQueue) Insert(transaction EthereumRawTransaction) {
	f.Tail = f.Tail + 1
	if f.Tail > 999 {
		f.Tail = 0
	}
	f.Queue[f.Tail] = transaction
}
