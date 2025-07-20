import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactNode } from "react";

// Hoist mock setup
const { mockGet, mockPost } = vi.hoisted(() => {
  const mockGet = vi.fn();
  const mockPost = vi.fn();
  return { mockGet, mockPost };
});

// Mock axios before any imports that use it
vi.mock("axios", () => ({
  default: {
    create: vi.fn(() => ({
      get: mockGet,
      post: mockPost,
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    })),
  },
}));

// Now import services after mocking axios
import { ghlService, useGHLPost } from "../services/ghlService";
import {
  googleAdsService,
  useGoogleAdsPerformance,
} from "../services/googleAdsService";

// Helper to create wrapper
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe("GHL Service", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe("authenticateGHL", () => {
    it("should authenticate and store API key", async () => {
      const mockApiKey = "test-api-key";
      
      // Mock successful API response
      mockGet.mockResolvedValueOnce({ status: 200, data: { user: "test" } });

      const result = await ghlService.authenticateGHL(mockApiKey);

      expect(result).toEqual({ success: true });
      expect(localStorage.getItem("ghlApiKey")).toBe(mockApiKey);
      expect(mockGet).toHaveBeenCalledWith("/v1/users/me", {
        headers: { Authorization: `Bearer ${mockApiKey}` },
      });
    });

    it("should handle invalid API key", async () => {
      // Mock failed API response
      mockGet.mockRejectedValueOnce(new Error("Unauthorized"));
      
      await expect(ghlService.authenticateGHL("invalid-key")).rejects.toThrow(
        "Invalid API key",
      );
      expect(localStorage.getItem("ghlApiKey")).toBe(null);
    });
  });

  describe("postContent", () => {
    it("should post content successfully", async () => {
      const content = {
        text: "Test post",
        scheduleDate: new Date("2024-01-20T10:00:00"),
      };

      const result = await ghlService.postContent("instagram", content);

      expect(result).toMatchObject({
        success: true,
        platform: "instagram",
        postId: expect.stringMatching(/^post_/),
        scheduledAt: content.scheduleDate.toISOString(),
      });
    });
  });

  describe("useGHLPost hook", () => {
    it("should handle successful post", async () => {
      const { result } = renderHook(() => useGHLPost(), {
        wrapper: createWrapper(),
      });

      const content = {
        text: "Test content",
        scheduleDate: new Date(),
      };

      result.current.mutate({ platform: "twitter", content });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });
    });
  });
});

describe("Google Ads Service", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getCampaignPerformance", () => {
    it("should return mock campaign data", async () => {
      const result = await googleAdsService.getCampaignPerformance();

      expect(result).toMatchObject({
        campaigns: expect.arrayContaining([
          expect.objectContaining({
            campaignId: expect.any(String),
            cluster: expect.any(String),
            impressions: expect.any(Number),
            performanceScore: expect.any(Number),
          }),
        ]),
        totalBudget: 10000,
        budgetUtilization: expect.any(Number),
      });
    });
  });

  describe("rotateBudget", () => {
    it("should rotate budget successfully", async () => {
      const result = await googleAdsService.rotateBudget(
        "camp_001",
        "New Cluster",
      );

      expect(result).toMatchObject({
        success: true,
        oldCampaignId: "camp_001",
        newCampaignId: expect.stringMatching(/^camp_/),
        budgetTransferred: expect.any(Number),
        message: expect.stringContaining("Successfully rotated budget"),
      });
    });
  });

  describe("useGoogleAdsPerformance hook", () => {
    it("should fetch performance data", async () => {
      const { result } = renderHook(() => useGoogleAdsPerformance(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
        expect(result.current.data).toBeDefined();
        expect(result.current.data?.campaigns).toHaveLength(4);
      });
    });
  });
});
