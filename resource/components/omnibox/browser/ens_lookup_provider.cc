// Copyright 2022 The CYFS Browser Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "components/omnibox/browser/ens_lookup_provider.h"

#include "base/i18n/case_conversion.h"
#include "base/strings/string_split.h"
#include "base/strings/string_util.h"
#include "base/strings/string_piece.h"
#include "base/strings/strcat.h"
#include "base/strings/utf_string_conversions.h"
#include "components/omnibox/browser/autocomplete_match_classification.h"
#include "components/omnibox/browser/tab_matcher.h"

#if !BUILDFLAG(IS_ANDROID) && !BUILDFLAG(IS_IOS)
#include "content/public/browser/web_contents.h"
#endif

EnsLookupProvider::EnsLookupProvider(AutocompleteProviderClient* client)
    : AutocompleteProvider(AutocompleteProvider::TYPE_OPEN_TAB),
      client_(client) {}

EnsLookupProvider::~EnsLookupProvider() = default;

void EnsLookupProvider::Start(const AutocompleteInput& input,
                            bool minimal_changes) {
  VLOG(1) << "EnsLookupProvider::Start, input info " << static_cast<int>(input.focus_type())
          << " input.text() " << input.text();
  matches_.clear();
  if (input.focus_type() != OmniboxFocusType::DEFAULT || input.text().empty()) {
    return;
  }

#if !BUILDFLAG(IS_ANDROID) && !BUILDFLAG(IS_IOS)
  auto input_text = base::TrimWhitespace(input.text(), base::TrimPositions::TRIM_ALL);
  VLOG(1) << "input_text - " << input_text;
  const size_t first_white(input_text.find_first_of(base::kWhitespaceUTF16));
  if (first_white != std::u16string::npos) {
    return;
  }
 
  const char16_t kEnsHostSuffixUTF16[] = u".eth";
  const char16_t kEnsHostSuffixnAndSlashUTF16[] = u".eth/";
  std::size_t ens_pos = input_text.find(kEnsHostSuffixnAndSlashUTF16);
  if (ens_pos != std::u16string::npos || base::EndsWith(input_text, kEnsHostSuffixUTF16)) {
    size_t invaild_ens_pos = input_text.rfind(u"/", ens_pos);
    if (invaild_ens_pos != std::u16string::npos) {
      VLOG(1) << "Find '/' before ens host keyword";
      return;
    }
    // std::string guess_url_string = "http://ipfs.eth";
    std::u16string guess_url_string = base::StrCat({base::StringPiece16(u"http://"), input_text});
    VLOG(1) << "EnsLookupProvider guess " << guess_url_string << " from " << input.text();
    matches_.push_back(
      CreateEnsLookupMatch(input.text(), std::u16string(), GURL(guess_url_string)));
  }
#endif  // !BUILDFLAG(IS_ANDROID) && !BUILDFLAG(IS_IOS)
}

AutocompleteMatch EnsLookupProvider::CreateEnsLookupMatch(
    const std::u16string& input_text,
    const std::u16string& title,
    const GURL& url) {
  VLOG(1) << "AutocompleteMatch EnsLookupProvider::CreateEnsLookupMatch";
  DCHECK(url.is_valid());

  constexpr int kOpenTabScore = 1500;
  AutocompleteMatch match(this, kOpenTabScore,
                          /*deletable=*/false, AutocompleteMatchType::OPEN_TAB);

  match.destination_url = url;
  match.allowed_to_be_default_match = true;
  match.contents = base::UTF8ToUTF16(url.spec());
  auto contents_terms = FindTermMatches(input_text, match.contents);
  match.contents_class = ClassifyTermMatches(
      contents_terms, match.contents.size(),
      ACMatchClassification::MATCH | ACMatchClassification::URL,
      ACMatchClassification::URL);

  match.description = title;
  auto description_terms = FindTermMatches(input_text, match.description);
  match.description_class = ClassifyTermMatches(
      description_terms, match.description.size(), ACMatchClassification::MATCH,
      ACMatchClassification::NONE);

  return match;
}
