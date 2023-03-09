// Copyright 2022 The CYFS Browser Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef COMPONENTS_OMNIBOX_BROWSER_ENS_LOOKUP_PROVIDER_H_
#define COMPONENTS_OMNIBOX_BROWSER_ENS_LOOKUP_PROVIDER_H_

#include "base/memory/raw_ptr.h"
#include "components/omnibox/browser/autocomplete_input.h"
#include "components/omnibox/browser/autocomplete_match.h"
#include "components/omnibox/browser/autocomplete_provider.h"
#include "components/omnibox/browser/autocomplete_provider_client.h"

// This provider matches user input against open tabs. It is *not* included as a
// default provider.
class EnsLookupProvider : public AutocompleteProvider {
 public:
  explicit EnsLookupProvider(AutocompleteProviderClient* client);

  EnsLookupProvider(const EnsLookupProvider&) = delete;
  EnsLookupProvider& operator=(const EnsLookupProvider&) = delete;

  void Start(const AutocompleteInput& input, bool minimal_changes) override;

 private:
  ~EnsLookupProvider() override;

  AutocompleteMatch CreateEnsLookupMatch(const std::u16string& input_text,
                                       const std::u16string& title,
                                       const GURL& url);

  raw_ptr<AutocompleteProviderClient> client_;
};

#endif  // COMPONENTS_OMNIBOX_BROWSER_ENS_LOOKUP_PROVIDER_H_
