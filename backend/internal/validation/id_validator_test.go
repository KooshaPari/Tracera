package validation

import (
	"testing"
)

func TestValidateUUID(t *testing.T) {
	tests := []struct {
		name    string
		uuid    string
		wantErr bool
	}{
		{
			name:    "valid lowercase UUID",
			uuid:    "123e4567-e89b-12d3-a456-426614174000",
			wantErr: false,
		},
		{
			name:    "valid uppercase UUID",
			uuid:    "123E4567-E89B-12D3-A456-426614174000",
			wantErr: false,
		},
		{
			name:    "valid UUID with spaces",
			uuid:    "  123e4567-e89b-12d3-a456-426614174000  ",
			wantErr: false,
		},
		{
			name:    "invalid UUID - too short",
			uuid:    "123e4567-e89b-12d3-a456-42661417400",
			wantErr: true,
		},
		{
			name:    "invalid UUID - missing dashes",
			uuid:    "123e4567e89b12d3a456426614174000",
			wantErr: true,
		},
		{
			name:    "invalid UUID - invalid characters",
			uuid:    "123g4567-e89b-12d3-a456-426614174000",
			wantErr: true,
		},
		{
			name:    "empty string",
			uuid:    "",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateUUID(tt.uuid)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidateUUID() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func TestNormalizeUUID(t *testing.T) {
	tests := []struct {
		name string
		uuid string
		want string
	}{
		{
			name: "uppercase to lowercase",
			uuid: "123E4567-E89B-12D3-A456-426614174000",
			want: "123e4567-e89b-12d3-a456-426614174000",
		},
		{
			name: "trim spaces",
			uuid: "  123e4567-e89b-12d3-a456-426614174000  ",
			want: "123e4567-e89b-12d3-a456-426614174000",
		},
		{
			name: "already normalized",
			uuid: "123e4567-e89b-12d3-a456-426614174000",
			want: "123e4567-e89b-12d3-a456-426614174000",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := NormalizeUUID(tt.uuid); got != tt.want {
				t.Errorf("NormalizeUUID() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestIsValidUUID(t *testing.T) {
	tests := []struct {
		name string
		uuid string
		want bool
	}{
		{
			name: "valid UUID",
			uuid: "123e4567-e89b-12d3-a456-426614174000",
			want: true,
		},
		{
			name: "invalid UUID",
			uuid: "invalid",
			want: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := IsValidUUID(tt.uuid); got != tt.want {
				t.Errorf("IsValidUUID() = %v, want %v", got, tt.want)
			}
		})
	}
}

func TestValidateUUIDs(t *testing.T) {
	tests := []struct {
		name    string
		uuids   []string
		wantErr bool
	}{
		{
			name: "all valid",
			uuids: []string{
				"123e4567-e89b-12d3-a456-426614174000",
				"223e4567-e89b-12d3-a456-426614174000",
			},
			wantErr: false,
		},
		{
			name: "one invalid",
			uuids: []string{
				"123e4567-e89b-12d3-a456-426614174000",
				"invalid",
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := ValidateUUIDs(tt.uuids...)
			if (err != nil) != tt.wantErr {
				t.Errorf("ValidateUUIDs() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}
