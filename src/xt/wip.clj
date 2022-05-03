(ns xt.wip
  (:require [xtdb.api :as xt]))

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
