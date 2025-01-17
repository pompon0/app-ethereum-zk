#include "manage_asset_info.h"
#include "shared_context.h"

void forget_known_assets(void) {
    memset(tmpCtx.transactionContext.assetSet, false, MAX_ASSETS);
    tmpCtx.transactionContext.currentAssetIndex = 0;
}

static extraInfo_t *get_asset_info(uint8_t index) {
    if (index >= MAX_ASSETS) {
        return NULL;
    }
    return &tmpCtx.transactionContext.extraInfo[index];
}

static bool asset_info_is_set(uint8_t index) {
    if (index >= MAX_ASSETS) {
        return false;
    }
    return tmpCtx.transactionContext.assetSet[index];
}

const tokenDefinition_t ZK_TOKEN = {
  {
    // real ZK sync contract on mainnet
    //  0x5a, 0x7d, 0x6b, 0x2f, 0x92, 0xc7, 0x7f, 0xad, 0x6c, 0xca,
    //  0xbd, 0x7e, 0xe0, 0x62, 0x4e, 0x64, 0x90, 0x7e, 0xaf, 0x3e
    
    //  fake ZK on sepolia
    0xf6, 0x2b, 0xe9, 0xc5, 0x68, 0xb0, 0x97, 0x9e, 0x02, 0x08,
    0xba, 0xff, 0xae, 0x3e, 0x59, 0x54, 0x43, 0xfa, 0x29, 0x98
  },
  {'Z','K'},
  18,
};

extraInfo_t *get_asset_info_by_addr(const uint8_t *contractAddress) {
    // Works for ERC-20 & NFT tokens since both structs in the union have the
    // contract address aligned
    for (uint8_t i = 0; i < MAX_ASSETS; i++) {
        extraInfo_t *currentItem = get_asset_info(i);
        if (asset_info_is_set(i) &&
            (memcmp(currentItem->token.address, contractAddress, ADDRESS_LENGTH) == 0)) {
            PRINTF("Token found at index %d\n", i);
            return currentItem;
        }
    }
    // If token was not found and it is the ZK token, then add it to the assets.
    if (memcmp(ZK_TOKEN.address, contractAddress, ADDRESS_LENGTH) == 0) {
      PRINTF("ZK HACK ACTIVATED\n");
      extraInfo_t *asset = get_current_asset_info();
      memmove(&asset->token,&ZK_TOKEN,sizeof(tokenDefinition_t));
      validate_current_asset_info();
      return asset;
    }

    return NULL;
}

extraInfo_t *get_current_asset_info(void) {
    return get_asset_info(tmpCtx.transactionContext.currentAssetIndex);
}

void validate_current_asset_info(void) {
    // mark it as set
    tmpCtx.transactionContext.assetSet[tmpCtx.transactionContext.currentAssetIndex] = true;
    // increment index
    tmpCtx.transactionContext.currentAssetIndex =
        (tmpCtx.transactionContext.currentAssetIndex + 1) % MAX_ASSETS;
}
