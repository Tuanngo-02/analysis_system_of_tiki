import { useState } from "react";
import { apiService } from "../services/api";
import "../styles/Features.css";

const compareKeys = [
  "comparison_points",
  "differences",
  "product_1_advantages",
  "product_2_advantages",
  "recommendation",
];

function parseJsonString(value) {
  if (typeof value !== "string") {
    return null;
  }

  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

function hasCompareData(value) {
  return (
    value &&
    typeof value === "object" &&
    compareKeys.some((key) => Object.prototype.hasOwnProperty.call(value, key))
  );
}

function findCompareData(value) {
  if (!value) {
    return null;
  }

  const parsed = parseJsonString(value);
  if (parsed) {
    return findCompareData(parsed);
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      const found = findCompareData(item);
      if (found) {
        return found;
      }
    }
    return null;
  }

  if (typeof value !== "object") {
    return null;
  }

  if (hasCompareData(value)) {
    return value;
  }

  const priorityKeys = ["data", "received", "result", "output", "body", "response"];
  for (const key of priorityKeys) {
    const found = findCompareData(value[key]);
    if (found) {
      return found;
    }
  }

  for (const nestedValue of Object.values(value)) {
    const found = findCompareData(nestedValue);
    if (found) {
      return found;
    }
  }

  return null;
}

function normalizeList(value) {
  if (!value) {
    return [];
  }

  if (Array.isArray(value)) {
    return value.filter(Boolean);
  }

  return [value];
}

function normalizeText(value) {
  return String(value)
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function deriveProductNames(items) {
  const firstPoint = formatCompareItem(items[0] || "");
  const detail = firstPoint.split(":").slice(1).join(":");
  const parts = splitComparisonDetail(detail);
  const cleanName = (part, fallback) => {
    const words = String(part || "")
      .trim()
      .split(/\s+/)
      .filter(Boolean);
    const laIndex = words.findIndex((word) => normalizeText(word) === "la");
    const nameWords = laIndex > 0 ? words.slice(0, laIndex) : words.slice(0, 2);
    return nameWords.join(" ").replace(/[,.]/g, "") || fallback;
  };

  return {
    product1: cleanName(parts[0], "San pham 1"),
    product2: cleanName(parts[1], "San pham 2"),
  };
}

function splitComparisonDetail(detail) {
  const normalized = normalizeText(detail);
  const separators = [" trong khi ", " so voi ", " con "];

  for (const separator of separators) {
    const index = normalized.indexOf(separator);
    if (index !== -1) {
      return [
        detail.slice(0, index).trim(),
        detail.slice(index + separator.length).trim(),
      ];
    }
  }

  return [detail.trim()];
}

function splitComparisonPoint(value, product1Name, product2Name) {
  const text = formatCompareItem(value);
  const separatorIndex = text.indexOf(":");

  if (separatorIndex === -1) {
    return {
      label: "Tieu chi",
      product1: text,
      product2: text,
    };
  }

  const label = text.slice(0, separatorIndex).trim();
  const details = text.slice(separatorIndex + 1).trim();
  const parts = splitComparisonDetail(details);

  if (parts.length >= 2) {
    const firstPart = parts[0].trim();
    const secondPart = parts.slice(1).join(" ").trim();
    const firstNormalized = normalizeText(firstPart);
    const secondNormalized = normalizeText(secondPart);
    const product1Normalized = normalizeText(product1Name);
    const product2Normalized = normalizeText(product2Name);

    if (
      firstNormalized.includes(product2Normalized) ||
      secondNormalized.includes(product1Normalized)
    ) {
      return {
        label,
        product1: secondPart,
        product2: firstPart,
      };
    }

    return {
      label,
      product1: firstPart,
      product2: secondPart,
    };
  }

  return {
    label,
    product1: details,
    product2: details,
  };
}

function formatCompareItem(value) {
  if (typeof value === "string") {
    return value;
  }

  if (value === null || value === undefined) {
    return "";
  }

  if (typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}

function ComparisonTable({ items, product1Label, product2Label }) {
  if (!items.length) {
    return null;
  }

  return (
    <section className="compare-difference-panel">
      <div className="compare-panel-heading">
        <span>Điểm khác nhau</span>
        <h4>So sánh theo từng tiêu chí</h4>
      </div>

      <div className="compare-difference-table">
        <div className="compare-difference-head compare-criterion-head">Tiêu chí</div>
        <div className="compare-difference-head">{product1Label}</div>
        <div className="compare-difference-head">{product2Label}</div>

        {items.map((item, index) => {
          const row = splitComparisonPoint(item, product1Label, product2Label);

          return (
            <div className="compare-difference-row" key={`difference-${index}`}>
              <div className="compare-criterion">{row.label}</div>
              <div className="compare-product-cell">{row.product1}</div>
              <div className="compare-product-cell">{row.product2}</div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function CompareList({ title, items, tone = "default" }) {
  if (!items.length) {
    return null;
  }

  return (
    <section className={`compare-section compare-section-${tone}`}>
      <div className="compare-section-icon">{tone === "product-one" ? "1" : "2"}</div>
      <h4>{title}</h4>
      <ul>
        {items.map((item, index) => (
          <li key={`${title}-${index}`}>{formatCompareItem(item)}</li>
        ))}
      </ul>
    </section>
  );
}

export function ComparePage() {
  const [productUrl1, setProductUrl1] = useState("");
  const [productUrl2, setProductUrl2] = useState("");
  const [compareResult, setCompareResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCompare = async (event) => {
    event.preventDefault();

    if (!productUrl1.trim() || !productUrl2.trim()) {
      setError("Vui long nhap du 2 link san pham Tiki");
      return;
    }

    setError("");
    setCompareResult(null);
    setLoading(true);

    try {
      const data = await apiService.getCompareProductApis(productUrl1, productUrl2);
      let compareData = findCompareData(data);
      console.log(data, "data");
      
      if (!compareData) {
        compareData = await waitForCompareData();
      }

      setCompareResult({
        raw: data,
        compareData,
      });
    } catch (err) {
      setError(err.message || "Loi khi so sanh san pham");
    } finally {
      setLoading(false);
    }
  };

  const waitForCompareData = async () => {
    for (let attempt = 0; attempt < 10; attempt += 1) {
      await new Promise((resolve) => setTimeout(resolve, 1000));

      try {
        const latestResult = await apiService.getCompareResult();
        console.log("latestResult:", latestResult);
        
        const compareData = findCompareData(latestResult);
        if (compareData) {
          return compareData;
        }
      } catch (err) {
        if (attempt === 9) {
          console.warn("No compare result from n8n yet", err);
        }
      }
    }

    return null;
  };

  const compareData = compareResult?.compareData;
  const rawData = compareResult?.raw;
  const comparisonPoints = normalizeList(
    compareData?.comparison_points || compareData?.differences
  );
  const derivedNames = deriveProductNames(comparisonPoints);
  const product1Label = compareData?.product_1_name || derivedNames.product1;
  const product2Label = compareData?.product_2_name || derivedNames.product2;
  const product1Advantages = normalizeList(compareData?.product_1_advantages);
  const product2Advantages = normalizeList(compareData?.product_2_advantages);

  return (
    <div className="feature-container">
      <div className="feature-header">
        <h2>So Sánh Sản Phẩm</h2>
        <p>Nhập 2 link sản phẩm Tiki để xem điểm khác nhau, ưu điểm và khuyến nghị</p>
      </div>

      <form onSubmit={handleCompare} className="feature-form compare-form">
        <div className="form-group">
          <label htmlFor="productUrl1">Link sản phẩm 1:</label>
          <input
            type="url"
            id="productUrl1"
            value={productUrl1}
            onChange={(event) => setProductUrl1(event.target.value)}
            placeholder="https://tiki.vn/...-p2738497.html?spid=..."
            required
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="productUrl2">Link sản phẩm 2:</label>
          <input
            type="url"
            id="productUrl2"
            value={productUrl2}
            onChange={(event) => setProductUrl2(event.target.value)}
            placeholder="https://tiki.vn/...-p123456.html?spid=..."
            required
            disabled={loading}
          />
        </div>

        <button type="submit" disabled={loading} className="analyze-btn">
          {loading ? "Dang so sanh..." : "So Sanh San Pham"}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      {compareResult && (
        <div className="result-container">
          <div className="result-card">
            <div className="result-header">
              <h3>Kết Quả So Sánh</h3>
              <span className="total-review">
                {compareData ? "Đã phân tích" : "Chưa có dữ liệu"}
              </span>
            </div>

            {compareData ? (
              <div className="compare-result-content">
                <ComparisonTable
                  items={comparisonPoints}
                  product1Label="Sản Phẩm 1"
                  product2Label="Sản Phẩm 2"
                />

                <div className="compare-advantages-grid">
                  <CompareList
                    title={`Ưu điểm Sản Phẩm 1`}
                    items={product1Advantages}
                    tone="product-one"
                  />
                  <CompareList
                    title={`Ưu điểm Sản Phẩm 2`}
                    items={product2Advantages}
                    tone="product-two"
                  />
                </div>

                {compareData.recommendation && (
                  <section className="compare-recommendation">
                    <h4>Khuyến nghị</h4>
                    <p>{compareData.recommendation}</p>
                  </section>
                )}
              </div>
            ) : (
              <div className="no-suggestions">
                Backend da tra ve ket qua, nhung frontend khong tim thay cac truong
                comparison_points, differences, product_1_advantages,
                product_2_advantages hoac recommendation.
              </div>
            )}
            <button
              className="reset-btn"
              onClick={() => {
                setCompareResult(null);
                setError("");
                setProductUrl1("");
                setProductUrl2("");
              }}
            >
              Nhap Link Khac
            </button>
          </div>
        </div>
      )}

      {!compareResult && !error && !loading && (
        <div className="info-box">
          <p>Link hop le can co doan pPRODUCT_ID.html trong URL san pham Tiki.</p>
        </div>
      )}
    </div>
  );
}
