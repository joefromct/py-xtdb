(ns xt.wip
  (:require [xtdb.api :as xt]))

(xt/status
 (xt/new-api-client (str "http://localhost:" 4001)))
