(ns xt.wip
  (:require [xtdb.api :as xt]
            [cheshire.core :as json]
            [clojure.string :as str]))

(comment
  (xt/status
   (xt/new-api-client (str "http://localhost:" 4001)))

  (xt/q (xt/db (xt/new-api-client (str "http://localhost:" 4001)) )
        '{:find [(pull ?id [*]) ]
          ;; :keys [date ]
          :where [[?id :xt/id]
                  ;; [?id :date ?date]
                  ]
          ;; :order-by [[?id :desc]]
          :limit 10})

  ;; I wanted some SIC codes to fake:
  (def jr (->> "https://www2.census.gov/programs-surveys/cbp/technical-documentation/records-layouts/sic-code-descriptions/sic88_97.txt"
               slurp
               ((fn [r] (str/split r #"\n")))
               (drop 1)
               (map (fn [r]
                      (let [sic  (str/trim (subs r 0 4))
                            desc (str/trim (subs r 5  ))]

                        {:sic  sic
                         :desc desc
                         :numeric? (when (re-find #"^\d+$" sic) true)})))))

  (spit ".data/sic-codes.json"
        (json/generate-string jr {:pretty true}))
  ,)
