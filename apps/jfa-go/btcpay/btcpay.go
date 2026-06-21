// Package btcpay is a minimal client for the BTCPay Server Greenfield API,
// covering just what jfa-go needs: creating/fetching store invoices and
// verifying webhook signatures.
package btcpay

import (
	"bytes"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"strings"
	"time"
)

// Client talks to a single BTCPay Server store.
type Client struct {
	server        string
	apiKey        string
	storeID       string
	webhookSecret string
	http          *http.Client
}

// NewClient returns a client for the given server (base URL), API key, store
// ID and webhook secret. The server may be given with or without scheme.
func NewClient(server, apiKey, storeID, webhookSecret string) *Client {
	server = strings.TrimRight(server, "/")
	if !strings.HasPrefix(server, "http://") && !strings.HasPrefix(server, "https://") {
		server = "https://" + server
	}
	return &Client{
		server:        server,
		apiKey:        apiKey,
		storeID:       storeID,
		webhookSecret: webhookSecret,
		http:          &http.Client{Timeout: 30 * time.Second},
	}
}

// InvoiceCheckout holds the checkout options jfa-go sets when creating an
// invoice.
type InvoiceCheckout struct {
	RedirectURL           string `json:"redirectURL,omitempty"`
	RedirectAutomatically bool   `json:"redirectAutomatically,omitempty"`
}

// InvoiceRequest is the subset of the Greenfield create-invoice request used
// by jfa-go.
type InvoiceRequest struct {
	Amount   float64
	Currency string
	Metadata map[string]string
	Checkout *InvoiceCheckout
}

// wire is the on-the-wire form; Greenfield expects "amount" as a string.
type invoiceRequestWire struct {
	Amount   string            `json:"amount"`
	Currency string            `json:"currency"`
	Metadata map[string]string `json:"metadata,omitempty"`
	Checkout *InvoiceCheckout  `json:"checkout,omitempty"`
}

// Invoice is the subset of a BTCPay invoice that jfa-go consumes.
type Invoice struct {
	ID           string
	CheckoutLink string
	Status       string
	Metadata     map[string]string
}

// UnmarshalJSON tolerates non-string metadata values (BTCPay metadata is
// free-form JSON) by coercing each value to a string.
func (inv *Invoice) UnmarshalJSON(b []byte) error {
	var raw struct {
		ID           string                     `json:"id"`
		CheckoutLink string                     `json:"checkoutLink"`
		Status       string                     `json:"status"`
		Metadata     map[string]json.RawMessage `json:"metadata"`
	}
	if err := json.Unmarshal(b, &raw); err != nil {
		return err
	}
	inv.ID = raw.ID
	inv.CheckoutLink = raw.CheckoutLink
	inv.Status = raw.Status
	inv.Metadata = make(map[string]string, len(raw.Metadata))
	for k, v := range raw.Metadata {
		var s string
		if err := json.Unmarshal(v, &s); err == nil {
			inv.Metadata[k] = s
		} else {
			inv.Metadata[k] = strings.Trim(string(v), `"`)
		}
	}
	return nil
}

// WebhookEvent is the subset of a BTCPay webhook delivery jfa-go reacts to.
type WebhookEvent struct {
	Type      string `json:"type"`
	InvoiceID string `json:"invoiceId"`
	StoreID   string `json:"storeId"`
	Timestamp int64  `json:"timestamp"`
}

func (c *Client) do(method, url string, body []byte) ([]byte, error) {
	var rdr io.Reader
	if body != nil {
		rdr = bytes.NewReader(body)
	}
	req, err := http.NewRequest(method, url, rdr)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "token "+c.apiKey)
	req.Header.Set("Accept", "application/json")
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	resp, err := c.http.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return nil, fmt.Errorf("btcpay: %s %s: status %d: %s", method, url, resp.StatusCode, string(respBody))
	}
	return respBody, nil
}

// CreateInvoice creates a new invoice on the store.
func (c *Client) CreateInvoice(req InvoiceRequest) (*Invoice, error) {
	wire := invoiceRequestWire{
		Amount:   strconv.FormatFloat(req.Amount, 'f', -1, 64),
		Currency: req.Currency,
		Metadata: req.Metadata,
		Checkout: req.Checkout,
	}
	body, err := json.Marshal(wire)
	if err != nil {
		return nil, err
	}
	url := fmt.Sprintf("%s/api/v1/stores/%s/invoices", c.server, c.storeID)
	respBody, err := c.do(http.MethodPost, url, body)
	if err != nil {
		return nil, err
	}
	var inv Invoice
	if err := json.Unmarshal(respBody, &inv); err != nil {
		return nil, fmt.Errorf("btcpay: decode invoice: %w", err)
	}
	return &inv, nil
}

// GetInvoice fetches a single invoice by ID.
func (c *Client) GetInvoice(invoiceID string) (*Invoice, error) {
	url := fmt.Sprintf("%s/api/v1/stores/%s/invoices/%s", c.server, c.storeID, invoiceID)
	respBody, err := c.do(http.MethodGet, url, nil)
	if err != nil {
		return nil, err
	}
	var inv Invoice
	if err := json.Unmarshal(respBody, &inv); err != nil {
		return nil, fmt.Errorf("btcpay: decode invoice: %w", err)
	}
	return &inv, nil
}

// VerifyWebhookSignature checks the BTCPay-Sig header (HMAC-SHA256 of the raw
// body keyed with the webhook secret, formatted as "sha256=<hex>").
func (c *Client) VerifyWebhookSignature(payload []byte, sigHeader string) bool {
	if c.webhookSecret == "" || sigHeader == "" {
		return false
	}
	sig := strings.TrimSpace(strings.TrimPrefix(sigHeader, "sha256="))
	mac := hmac.New(sha256.New, []byte(c.webhookSecret))
	mac.Write(payload)
	expected := hex.EncodeToString(mac.Sum(nil))
	return hmac.Equal([]byte(expected), []byte(sig))
}

// ParseWebhookEvent decodes a webhook delivery body.
func ParseWebhookEvent(payload []byte) (*WebhookEvent, error) {
	var e WebhookEvent
	if err := json.Unmarshal(payload, &e); err != nil {
		return nil, err
	}
	if e.Type == "" {
		return nil, fmt.Errorf("btcpay: webhook payload missing type")
	}
	return &e, nil
}
