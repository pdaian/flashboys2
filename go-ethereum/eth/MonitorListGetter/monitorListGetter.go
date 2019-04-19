package MonitorListGetter

import (
	"net/http"
	"encoding/json"
	"crypto/x509"
	"fmt"
	"crypto/tls"
	"io/ioutil"
	"time"
	"strings"
)


var listVersion = 0
var MonitoredAddressesMap = make(map[string]bool)
var pemData = []byte(`-----BEGIN CERTIFICATE-----
MIIFUDCCBDigAwIBAgISBET05bK2NYz37HjqBjitv+fAMA0GCSqGSIb3DQEBCwUA
MEoxCzAJBgNVBAYTAlVTMRYwFAYDVQQKEw1MZXQncyBFbmNyeXB0MSMwIQYDVQQD
ExpMZXQncyBFbmNyeXB0IEF1dGhvcml0eSBYMzAeFw0xOTAxMDMyMDUzMzhaFw0x
OTA0MDMyMDUzMzhaMBcxFTATBgNVBAMTDG5vbXMua2VsbC5pbzCCASIwDQYJKoZI
hvcNAQEBBQADggEPADCCAQoCggEBAJ+R/m55FYrqxYEfxdvl4NwZ+lfAAbzp+KC9
8AIhDNKtp6WUFdwlVFYXKFjBiQRebRZaC1zvlfvtb3WfHVROgXQ0OaR+aORpUneQ
EEqL+/sZFyZMoexKtqkpSe1cgqBT8KVi0RPpfvDcmAzMqVzNzg8PLedLMOwDovXu
+60513rWeJf7x1ew0q/V9uVDyi2RliOtoq+hgu5wTBXCq+jE0KbxOP2s2l7Mn6bl
EQRmGWVIzkBJGU3nxom9I5t9YLjQODNdbar31ntIiJ0PIN2b+MAfpeaZlSzVdXty
TRXa466fZgRroPmqmDb7OTHLqRwiYx3pWvazyx4+TT35JEEcrlMCAwEAAaOCAmEw
ggJdMA4GA1UdDwEB/wQEAwIFoDAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUH
AwIwDAYDVR0TAQH/BAIwADAdBgNVHQ4EFgQUlshe65Pk1ePf/sVEFi1jNDPUTBgw
HwYDVR0jBBgwFoAUqEpqYwR93brm0Tm3pkVl7/Oo7KEwbwYIKwYBBQUHAQEEYzBh
MC4GCCsGAQUFBzABhiJodHRwOi8vb2NzcC5pbnQteDMubGV0c2VuY3J5cHQub3Jn
MC8GCCsGAQUFBzAChiNodHRwOi8vY2VydC5pbnQteDMubGV0c2VuY3J5cHQub3Jn
LzAXBgNVHREEEDAOggxub21zLmtlbGwuaW8wTAYDVR0gBEUwQzAIBgZngQwBAgEw
NwYLKwYBBAGC3xMBAQEwKDAmBggrBgEFBQcCARYaaHR0cDovL2Nwcy5sZXRzZW5j
cnlwdC5vcmcwggEEBgorBgEEAdZ5AgQCBIH1BIHyAPAAdgB0ftqDMa0zEJEhnM4l
T0Jwwr/9XkIgCMY3NXnmEHvMVgAAAWgVtSH1AAAEAwBHMEUCIQDqh07J0LWvHxyD
ajDmYc6aYtOMPu2iksUJvMctjcjYFgIgR40U7bqruAt7imwa3XUNJV55D/zyDo0I
nYW+++R+yAkAdgApPFGWVMg5ZbqqUPxYB9S3b79Yeily3KTDDPTlRUf0eAAAAWgV
tSQCAAAEAwBHMEUCIHVxF5RekfdmWstC0qTsm7/Dy14Cz/qhUu+p3QGupLSAAiEA
tjSBRApuRSEiOyKPHmy8fwDRGGtxaV4gbC0I11I0vQAwDQYJKoZIhvcNAQELBQAD
ggEBAHQlEDBohg4/cokMVtQ/+JfaMDwyuNALnpOhvrD5v8KF2n9CeRYH2PPhg2j7
Ts9QCNKiacUMFvnr5ddIS/3EU3gAlqYS0Ut5RLqaQ3+8kIv3UUOl7XcQrwYz1ETy
U4oJFK9aO3GDdfxuvQ042+ceeokd6BK6LWMEbOI4XFrbcY+kq0TrccZBlHu3rH4T
5vYQQv9BmCaxyMb5sZbX8BcWResRZPYTGh88YTBA2/gEYwVBSmlOddB266HKepdg
5WOce7yz260GIX4un8EuVSFTiusi/I4R7YRz+2NhsXMraEjjPIr63AdG6EDqZKnT
jgl1Hz7mkr9xOaT4ohxWAnqTr8M=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIEkjCCA3qgAwIBAgIQCgFBQgAAAVOFc2oLheynCDANBgkqhkiG9w0BAQsFADA/
MSQwIgYDVQQKExtEaWdpdGFsIFNpZ25hdHVyZSBUcnVzdCBDby4xFzAVBgNVBAMT
DkRTVCBSb290IENBIFgzMB4XDTE2MDMxNzE2NDA0NloXDTIxMDMxNzE2NDA0Nlow
SjELMAkGA1UEBhMCVVMxFjAUBgNVBAoTDUxldCdzIEVuY3J5cHQxIzAhBgNVBAMT
GkxldCdzIEVuY3J5cHQgQXV0aG9yaXR5IFgzMIIBIjANBgkqhkiG9w0BAQEFAAOC
AQ8AMIIBCgKCAQEAnNMM8FrlLke3cl03g7NoYzDq1zUmGSXhvb418XCSL7e4S0EF
q6meNQhY7LEqxGiHC6PjdeTm86dicbp5gWAf15Gan/PQeGdxyGkOlZHP/uaZ6WA8
SMx+yk13EiSdRxta67nsHjcAHJyse6cF6s5K671B5TaYucv9bTyWaN8jKkKQDIZ0
Z8h/pZq4UmEUEz9l6YKHy9v6Dlb2honzhT+Xhq+w3Brvaw2VFn3EK6BlspkENnWA
a6xK8xuQSXgvopZPKiAlKQTGdMDQMc2PMTiVFrqoM7hD8bEfwzB/onkxEz0tNvjj
/PIzark5McWvxI0NHWQWM6r6hCm21AvA2H3DkwIDAQABo4IBfTCCAXkwEgYDVR0T
AQH/BAgwBgEB/wIBADAOBgNVHQ8BAf8EBAMCAYYwfwYIKwYBBQUHAQEEczBxMDIG
CCsGAQUFBzABhiZodHRwOi8vaXNyZy50cnVzdGlkLm9jc3AuaWRlbnRydXN0LmNv
bTA7BggrBgEFBQcwAoYvaHR0cDovL2FwcHMuaWRlbnRydXN0LmNvbS9yb290cy9k
c3Ryb290Y2F4My5wN2MwHwYDVR0jBBgwFoAUxKexpHsscfrb4UuQdf/EFWCFiRAw
VAYDVR0gBE0wSzAIBgZngQwBAgEwPwYLKwYBBAGC3xMBAQEwMDAuBggrBgEFBQcC
ARYiaHR0cDovL2Nwcy5yb290LXgxLmxldHNlbmNyeXB0Lm9yZzA8BgNVHR8ENTAz
MDGgL6AthitodHRwOi8vY3JsLmlkZW50cnVzdC5jb20vRFNUUk9PVENBWDNDUkwu
Y3JsMB0GA1UdDgQWBBSoSmpjBH3duubRObemRWXv86jsoTANBgkqhkiG9w0BAQsF
AAOCAQEA3TPXEfNjWDjdGBX7CVW+dla5cEilaUcne8IkCJLxWh9KEik3JHRRHGJo
uM2VcGfl96S8TihRzZvoroed6ti6WqEBmtzw3Wodatg+VyOeph4EYpr/1wXKtx8/
wApIvJSwtmVi4MFU5aMqrSDE6ea73Mj2tcMyo5jMd6jmeWUHK8so/joWUoHOUgwu
X4Po1QYz+3dszkDqMp4fklxBwXRsW10KXzPMTZ+sOPAveyxindmjkW8lGy+QsRlG
PfZ+G6Z6h7mjem0Y+iWlkYcV4PIWL1iwBi8saCbGS5jN2p8M+X+Q7UNKEkROb3N6
KOqkqm57TH2H3eDJAkSnh6/DNFu0Qg==
-----END CERTIFICATE-----`)

func PollAddressWatchList() {
	for {
		certs := x509.NewCertPool()
		certs.AppendCertsFromPEM(pemData)

		client := &http.Client{
			Transport: &http.Transport{
				TLSClientConfig: &tls.Config{
					RootCAs: certs,
				},
			},
		}

        req, err := http.NewRequest("POST", "https://REDACTED/lolgetsomeaddresses", strings.NewReader(fmt.Sprintf("version=%d&", listVersion)))
		if err != nil {
			fmt.Println("There was an error, trying to create an HTTP Request to send to the address server")
			fmt.Println(err)
		}
		req.SetBasicAuth("bro", "thisissecureiswear")
		req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
		//fmt.Printf("--> %s\n\n", formatRequest(req))
		resp, err := client.Do(req)
		if err != nil {
			fmt.Println("There was an error, trying to download the address list from the address server")
			fmt.Println(err)
			panic(resp)
		}

		body, err := ioutil.ReadAll(resp.Body)
		fmt.Printf("body: %s", string(body))
		if err != nil {
			fmt.Println("There was an error, trying to read the HTTP response from the address list server")
			fmt.Println(err)
		}

		type AddressList struct {
			Listy []string
			ListVersion int
		}

		var ReceivedAddressList AddressList

		err = json.Unmarshal(body, &ReceivedAddressList)
		if err != nil {
			fmt.Println("There was an error, trying to unmarshal JSON from the address list server")
			fmt.Println(err)
		}

		fmt.Println(ReceivedAddressList.Listy)
		fmt.Printf("List version = %d\n", ReceivedAddressList.ListVersion)
		listVersion = ReceivedAddressList.ListVersion
		for _, addr := range ReceivedAddressList.Listy {
			MonitoredAddressesMap[addr] = false
		}
		time.Sleep(15* time.Minute)
	}
}



// formatRequest generates ascii representation of a request
func formatRequest(r *http.Request) string {
	// Create return string
	var request []string

	// Add the request string
	url := fmt.Sprintf("%v %v %v", r.Method, r.URL, r.Proto)
	request = append(request, url)

	// Add the host
	request = append(request, fmt.Sprintf("Host: %v", r.Host))

	// Loop through headers
	for name, headers := range r.Header {
		name = strings.ToLower(name)
		for _, h := range headers {
			request = append(request, fmt.Sprintf("%v: %v", name, h))
		}
	}

	// If this is a POST, add post data
	if r.Method == "POST" {
		r.ParseForm()
		request = append(request, "\n")
		request = append(request, r.Form.Encode())
	}

	// Return the request as a string
	return strings.Join(request, "\n")
}

func SendAddressToMonitor(newAddr string) {
	certs := x509.NewCertPool()
	certs.AppendCertsFromPEM(pemData)

	client := &http.Client{
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{
				RootCAs: certs,
			},},}
	// body := bytes.NewBufferString(form.Encode())
	// body := bytes.NewBuffer([]byte(fmt.Sprintf("updateList=%s", newAddr)))
	req, err := http.NewRequest("POST", "https://REDACTED/lolpostsomeaddressses", strings.NewReader(fmt.Sprintf("updateList=%s&", newAddr)))
	// req.Header.Add("Content-Type", "multipart/form-data")
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	if err != nil {
		fmt.Printf("flashboys2 ERROR ERROR couldn't push a new address to the manage addr list endpoint %s", req.Form.Encode() )
	}
	req.SetBasicAuth("bro", "thisissecureiswear")
	// fmt.Printf("--> %s\n\n", formatRequest(req))
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("There was an error, trying to download the address list from the address server")
		fmt.Println(err)
	}
	body2, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("There was an error, trying to read the HTTP response from the address list server")
		fmt.Println(err)
	}
	fmt.Println(string(body2))
}
