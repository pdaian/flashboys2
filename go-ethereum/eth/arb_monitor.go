package eth

import (
	"database/sql"
	"encoding/hex"
	"fmt"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/eth/CircularBufferQueue"
	"github.com/ethereum/go-ethereum/eth/MonitorListGetter"
	"github.com/ethereum/go-ethereum/log"
	_ "github.com/lib/pq"
	"io/ioutil"
	"os"
	"strings"
	"unicode"
	"math/big"
)

var ArbDB *sql.DB

var txCache CircularBufferQueue.FIFOTransactionQueue
var txCachePtr = &txCache

func InitTxCache() {
	txCachePtr.New()
}

func InitArbDB() {
	var err error
	homepath := os.Getenv("HOME")
	var connStrBuilder strings.Builder
	connStrBuilder.WriteString("user=flashboys2 password='lolsosecure' host='some.random.domain.us-west-2.rds.amazonaws.com' dbname=arbitrage sslmode=verify-ca sslrootcert=")
	connStrBuilder.WriteString(homepath)
	connStrBuilder.WriteString("/.postgresql/root.crt")
	ArbDB, err = sql.Open("postgres", connStrBuilder.String())
	if err != nil {
		log.Error(fmt.Sprintf("flashboys2 failed to connect to database: %s", err))

	}
	ArbDB.SetMaxOpenConns(15)
	err = ArbDB.Ping()

	if err != nil {
		log.Error(fmt.Sprintf("flashboys2 couldn't establish ping with the db: %s", err))
	} else {
		log.Info("DB connected successfully for initial ping.")
	}
}

func RemoveWhiteSpaceMap(str string) string {
	return strings.Map(func(r rune) rune {
		if unicode.IsSpace(r) {
			return -1
		}
		return r
	}, str)
}

func PullIPFromFile() (string, error) {
	ipBytes, fileErr := ioutil.ReadFile("/ipinfo.txt")
	if fileErr != nil {
		return "", fileErr
	}
	return RemoveWhiteSpaceMap(string(ipBytes)), nil
}

func SendLog(tx *types.Transaction, p *peer, pm *ProtocolManager, timeString string) {
	tempSigner := types.NewEIP155Signer(pm.chainconfig.ChainID)
	txSender, cryingerr := types.Sender(tempSigner, tx)
	var fromString, recipString, peerString, peerNameString, ipString string
	fromString = txSender.String()
	_, found := MonitorListGetter.MonitoredAddressesMap[strings.ToLower(fromString)] //  monitoredAddressesMap[strings.ToLower(fromString)]
	ipString = p.RemoteAddr().String()
	ipList := strings.Split(ipString, ":")
	ipStringSplit, ipPort := ipList[0], ipList[1]
	peerNameString = p.Name()
	peerString = p.String()
	if tx.To() == nil {
		recipString = ""
	} else {
		recipString = tx.To().String()
	}
	myIP, ipErr := PullIPFromFile()
	txNonce := tx.Nonce()
	gprice := tx.GasPrice().String()
	glimit := tx.Gas()
	txAmount := tx.Value().String()
	txV, txR, txS := tx.RawSignatureValues()
	txVString := txV.String()
	txRString := txR.String()
	txSString := txS.String()
	txPayload := hex.EncodeToString(tx.Data())
	txHash := tx.Hash().Hex()
	var txStringStruct = CircularBufferQueue.EthereumRawTransaction{
		myIP,
		fromString,
		recipString,
		peerString,
		peerNameString,
		ipStringSplit,
		ipPort,
		timeString,
		txNonce,
		gprice,
		glimit,
		txAmount,
		txPayload,
		txVString,
		txRString,
		txSString,
		txHash,
	}
	duplicateHash := false
	var gasPriceFloor big.Int
	gasPriceFloorPtr, success := gasPriceFloor.SetString("100000000000", 10)
	if success == true {
		for counter := 0; counter < 1000; counter++ {
			if  found == false &&
			    txCachePtr.Queue[counter].FromString == fromString &&
				txCachePtr.Queue[counter].RecipString == recipString &&
				txCachePtr.Queue[counter].TxNonce == txNonce &&
				txCachePtr.Queue[counter].TxHash != txHash &&
				txCachePtr.Queue[counter].TxSString != txSString &&
				txCachePtr.Queue[counter].TxRString != txRString &&
				tx.GasPrice().Cmp(gasPriceFloorPtr) == 1 {

				log.Info(fmt.Sprintf("flashboys2 new gas replacement event found: %s and %s have the same sender and Nonce, Sender is %s, recipient is %s, and gas price is %d", txHash, txCachePtr.Queue[counter].TxHash, fromString, recipString, gprice))
				found = true
				MonitorListGetter.SendAddressToMonitor(fromString)
				MonitorListGetter.MonitoredAddressesMap[strings.ToLower(fromString)]  = false
			}
			if found == true && txCachePtr.Queue[counter].TxHash == txHash {
				log.Info(fmt.Sprintf("flashboys2 duplicate TX: %s", txHash))
				duplicateHash = true
			}
		}
	} else {
		errmsg := fmt.Sprintf("flashboys2 failed to make an int for gasprice")
		log.Error(errmsg)
	}
	txCachePtr.Insert(txStringStruct)

	if found {
		if cryingerr == nil && ipErr == nil {
			if !duplicateHash {
				debugOutput := fmt.Sprintf(
					"flashboys2 my ip: %s time: %s | from: %s | to: %s | %s | Peer Name: %s | IP: %s | Port: %s | Nonce: %d | GasPrice: %s | GasLimit: %d | Value: %d | EC_V: %d | EC_R: %d | EC_S %d | Hash: %s | Payload: %s",
					myIP, timeString, fromString, recipString, peerString, peerNameString, ipStringSplit, ipPort, txNonce, gprice, glimit, txAmount, txV, txR, txS, txHash, txPayload)
				log.Info(debugOutput)

				dbQuery := `INSERT INTO arbitrage(monitor_ip, sender, reciever, peer_info, peer_name, ip_addr, port, time_seen, account_nonce, gas_price, gas_limit, amount, payload, ec_v, ec_r, ec_s, hash) 
				   VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17) RETURNING time_seen;`
				_, err := ArbDB.Exec(dbQuery,
					myIP, fromString, recipString, peerString, peerNameString, ipStringSplit, ipPort, timeString, txNonce, gprice, glimit, txAmount, txPayload, txVString, txRString, txSString, txHash)
				if err != nil {
					errmsg := fmt.Sprintf("flashboys2 failed to push data to the database: %s", err)
					log.Error(errmsg)
				}
			} else {
				debugOutput := fmt.Sprintf(
					"flashboys2 duplicate hash: %s time: %s | from: %s | to: %s | %s | Peer Name: %s | IP: %s | Port: %s | Nonce: %d | GasPrice: %s | GasLimit: %d | Value: %d | EC_V: %d | EC_R: %d | EC_S %d | Hash: %s | Payload: %s",
					myIP, timeString, fromString, recipString, peerString, peerNameString, ipStringSplit, ipPort, txNonce, gprice, glimit, txAmount, txV, txR, txS, txHash, txPayload)
				log.Info(debugOutput)
				dbQuery := `INSERT INTO arbitrage(monitor_ip, ip_addr, time_seen, hash) 
				   VALUES($1,$2,$3,$4) RETURNING time_seen;`
				_, err := ArbDB.Exec(dbQuery,
					myIP, ipStringSplit, timeString, txHash)
				if err != nil {
					errmsg := fmt.Sprintf("flashboys2 failed to push duplicate TX to the database: %s", err)
					log.Error(errmsg)
				}
			}

		}
	}
}

func SendLogNewBlock(hash common.Hash, number uint64, p *peer, timeString string) {
	var peerString, peerNameString, ipString string
	ipString = p.RemoteAddr().String()
	ipList := strings.Split(ipString, ":")
	ipStringSplit, ipPort := ipList[0], ipList[1]
	peerNameString = p.Name()
	peerString = p.String()
	myIP, ipErr := PullIPFromFile()
	bhash := hash.Hex()
	if ipErr == nil {
		debugOutput := fmt.Sprintf(
			"flashboys2 new block seen my ip: %s time: %s | %s | Peer Name: %s | IP: %s | Port: %s | Hash %s | Block Number %d",
			myIP, timeString, peerString, peerNameString, ipStringSplit, ipPort, bhash, number)
		log.Info(debugOutput)

		dbQuery := `INSERT INTO blocks(monitor_ip, time_seen, hash) 
			   VALUES($1,$2,$3);`
		_, err := ArbDB.Exec(dbQuery,
			myIP, timeString, bhash)
		if err != nil {
			errmsg := fmt.Sprintf("flashboys2 failed to push data to the database: %s", err)
			log.Error(errmsg)
		}
	}
}
