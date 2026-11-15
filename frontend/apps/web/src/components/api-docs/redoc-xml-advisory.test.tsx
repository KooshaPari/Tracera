import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RedocWrapper } from "./redoc-wrapper";

describe("ReDoc XML response", () => {
  it("renders an OpenAPI operation with an XML response schema", async () => {
    render(
      <RedocWrapper
        disableSearch
        spec={{
          openapi: "3.0.3",
          info: { title: "Widget Catalog", version: "1.0.0" },
          paths: {
            "/widgets": {
              get: {
                summary: "List widgets",
                responses: {
                  "200": {
                    description: "Widget response",
                    content: {
                      "application/xml": {
                        schema: {
                          type: "object",
                          xml: { name: "widget" },
                          properties: { name: { type: "string", example: "example" } },
                        },
                      },
                    },
                  },
                },
              },
            },
          },
        }}
      />,
    );
    expect(await screen.findByText("List widgets", {}, { timeout: 15000 })).toBeInTheDocument();
    expect(screen.getByText("Widget Catalog")).toBeInTheDocument();
  });
});
